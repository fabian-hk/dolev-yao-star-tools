#!/usr/bin/env python3
"""Discover Lean imports, verify files sequentially, and record wall-clock times.

Requires Python 3.9+ and the project's Lake toolchain. Run from the Lean project:
    python3 /path/to/dystar_tool.py benchmark
    python3 /path/to/dystar_tool.py benchmark --project-only --csv /tmp/times.csv
    python3 /path/to/dystar_tool.py benchmark Web/URL.lean --graph-only

By default, roots are all project .lean files (including Examples), excluding
hidden directories and lakefile.lean. Their transitive workspace dependencies
are included; precompiled Lean toolchain sources are excluded. --project-only
keeps dependencies in the graph but only times project files.

Each file's imports are prepared with `lake build FILE:deps` outside the timer.
The timed `lake lean FILE` invocation always elaborates the source, even when
its .olean is current. Seconds include Lake/process startup and importing
compiled dependencies, but exclude dependency preparation. Files are checked
sequentially to avoid contention. This accepts Lean's usual `sorry` warnings;
an "ok" row means elaboration succeeded, not that the file is axiom-free.
"""

import argparse
import csv
import graphlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


def captured(command, project, env=None):
    """Run a discovery command, retaining useful diagnostics on failure."""
    result = subprocess.run(command, cwd=project, env=env, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"Command failed: {command!r}\n{result.stdout}{result.stderr}")
    return result.stdout


def inside(path, directory):
    return path == directory or directory in path.parents


def project_sources(project):
    """Find project sources without traversing caches or version-control data."""
    sources = []
    for directory, subdirs, files in os.walk(project):
        subdirs[:] = sorted(name for name in subdirs if not name.startswith('.'))
        for name in sorted(files):
            if name.endswith('.lean') and name != 'lakefile.lean':
                sources.append((Path(directory) / name).resolve())
    return sorted(sources)


def dependency_graph(roots, project, env, lean, toolchain):
    """Ask Lean to parse imports, then follow their resolved source paths."""
    graph = {}
    pending = list(roots)
    while pending:
        source = pending.pop()
        if source in graph:
            continue
        output = captured([lean, '--src-deps', str(source)], project, env)
        dependencies = set()
        for line in output.splitlines():
            if not line.strip():
                continue
            dependency = Path(line.strip())
            if not dependency.is_absolute():
                dependency = project / dependency
            dependency = dependency.resolve()
            if inside(dependency, toolchain):
                continue
            if not dependency.is_file() or dependency.suffix != '.lean':
                raise RuntimeError(f"Invalid dependency reported for {source}: {line}")
            dependencies.add(dependency)
        graph[source] = dependencies
        pending.extend(sorted(dependencies - graph.keys(), reverse=True))
    return graph


def display_path(path, project):
    return os.path.relpath(path, project)


def module_name(source, source_roots):
    for root in source_roots:
        if inside(source, root):
            return '.'.join(source.relative_to(root).with_suffix('').parts)
    return source.stem


def write_graph(destination, graph, selected, project):
    """Write a Graphviz graph whose arrows point from a file to its imports."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('w', encoding='utf-8') as output:
        output.write('digraph lean_dependencies {\n  rankdir=LR;\n')
        for source, dependencies in sorted(graph.items()):
            node = json.dumps(display_path(source, project), ensure_ascii=False)
            style = 'solid' if source in selected else 'dashed'
            output.write(f'  {node} [shape=box, style={style}];\n')
            for dependency in sorted(dependencies):
                target = json.dumps(display_path(dependency, project), ensure_ascii=False)
                output.write(f'  {node} -> {target};\n')
        output.write('}\n')


def verify(order, graph, selected, project, csv_path, log_dir, source_roots):
    """Prepare imports, time fresh elaboration, and flush each result to CSV."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    statuses = {}
    failures = 0
    fields = ['module', 'file', 'seconds', 'status', 'exit_code', 'dependencies', 'log']
    with csv_path.open('w', newline='', encoding='utf-8') as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        output.flush()
        files = [source for source in order if source in selected]
        for index, source in enumerate(files, 1):
            name = module_name(source, source_roots)
            log_path = log_dir / f'{index:04d}-{name}.log'
            row = dict(module=name, file=display_path(source, project), seconds='',
                       status='', exit_code='', dependencies=json.dumps([
                           display_path(dep, project) for dep in sorted(graph[source])
                       ]), log=str(log_path))
            blocked = [dep for dep in sorted(graph[source])
                       if dep in statuses and statuses[dep] != 'ok']
            print(f'[{index}/{len(files)}] {row["file"]}', flush=True)
            with log_path.open('w', encoding='utf-8') as log:
                if blocked:
                    row['status'] = 'blocked'
                    log.write('Failed dependencies:\n' + '\n'.join(str(dep) for dep in blocked))
                else:
                    log.write('Preparing imports (outside timer)\n')
                    log.flush()
                    preparation = subprocess.run(
                        ['lake', 'build', f'{source}:deps'], cwd=project,
                        stdout=log, stderr=subprocess.STDOUT,
                    )
                    if preparation.returncode:
                        row.update(status='dependency_failed', exit_code=preparation.returncode)
                    else:
                        log.write('\nVerifying source (timed)\n')
                        log.flush()
                        start = time.perf_counter()
                        result = subprocess.run(
                            ['lake', 'lean', str(source)], cwd=project,
                            stdout=log, stderr=subprocess.STDOUT,
                        )
                        elapsed = time.perf_counter() - start
                        row.update(seconds=f'{elapsed:.6f}',
                                   status='ok' if result.returncode == 0 else 'failed',
                                   exit_code=result.returncode)
            statuses[source] = row['status']
            failures += row['status'] != 'ok'
            writer.writerow(row)
            output.flush()
            print(f'  {row["status"]}' + (f' ({row["seconds"]} s)' if row['seconds'] else ''), flush=True)
    return failures


def add_benchmark_arguments(parser):
    """Share benchmark options between the DYStar CLI and standalone script."""
    parser.add_argument('files', nargs='*', help='Optional root files, relative to the project')
    parser.add_argument('--csv', type=Path, default=Path('verification-times.csv'))
    parser.add_argument('--graph', type=Path, default=Path('dependency-graph.dot'))
    parser.add_argument('--log-dir', type=Path, default=Path('.lake/verification-logs'))
    parser.add_argument('--project-only', action='store_true', help='Only time files in this project')
    parser.add_argument('--graph-only', action='store_true', help='Write the graph without verifying files')
    parser.set_defaults(func=dystar_benchmark, benchmark_parser=parser)


def benchmark(args):
    """Benchmark the Lean project rooted in the invocation directory."""
    parser = args.benchmark_parser
    project = Path.cwd().resolve()
    if not any((project / name).is_file() for name in ['lakefile.toml', 'lakefile.lean']):
        parser.error(f'No Lake configuration in {project}')
    roots = sorted({(project / name).resolve() for name in args.files}) if args.files else project_sources(project)
    if not roots:
        parser.error('No Lean files found')
    for source in roots:
        if not source.is_file() or source.suffix != '.lean':
            parser.error(f'Not a Lean source file: {source}')
    # Obtain Lake's full environment once for dependency discovery, including
    # source paths for dependencies with custom srcDir values (e.g. Examples).
    env = json.loads(captured([
        'lake', 'env', sys.executable, '-c',
        'import json, os; print(json.dumps(dict(os.environ)))',
    ], project))
    lean = shutil.which('lean', path=env.get('PATH'))
    if not lean:
        raise RuntimeError('Lean not found in Lake environment')
    toolchain = Path(captured([lean, '--print-prefix'], project, env).strip()).resolve()
    source_roots = sorted({Path(path).resolve() for path in env.get('LEAN_SRC_PATH', '').split(os.pathsep)
                           if path}, key=lambda path: (-len(path.parts), str(path)))
    print(f'Discovering imports for {len(roots)} root files...', flush=True)
    graph = dependency_graph(roots, project, env, lean, toolchain)
    try:
        order = list(graphlib.TopologicalSorter(graph).static_order())
    except graphlib.CycleError as error:
        raise RuntimeError(f'Import cycle: {error.args[1]}') from error
    selected = {source for source in graph if not args.project_only or
                (inside(source, project) and '.lake' not in source.relative_to(project).parts)}
    # Resolve output paths relative to the invocation directory, as with other CLI tools.
    graph_path = args.graph.resolve()
    write_graph(graph_path, graph, selected, project)
    print(f'Graph: {graph_path} ({len(graph)} files; {len(selected)} selected)', flush=True)
    if args.graph_only:
        return 0
    failures = verify(order, graph, selected, project, args.csv.resolve(),
                      args.log_dir.resolve(), source_roots)
    print(f'CSV: {args.csv.resolve()} ({failures} failed or blocked files)', flush=True)
    return 1 if failures else 0


def dystar_benchmark(args):
    """CLI callback with the same diagnostics and exit codes as the script."""
    try:
        return benchmark(args)
    except (RuntimeError, OSError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print('Interrupted; completed CSV rows have been saved.', file=sys.stderr)
        return 130


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_benchmark_arguments(parser)
    return dystar_benchmark(parser.parse_args())


if __name__ == '__main__':
    sys.exit(main())
