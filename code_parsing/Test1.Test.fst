module Test1.Test1

open FStar.List.Tot

open DY.Core
open DY.Lib


#set-options "--fuel 0 --ifuel 0 --z3cliopt 'smt.qi.eager_threshold=100'"

(*
  This file contains helper functions for the 
  device authorization grant model.

*)

val verify_credentials:
  principal -> id -> bytes -> state_id -> traceful (option bool)
let verify_credentials authorization_server user password users_st =
  let search_fn = (fun cred -> cred.id.username = user.username && cred.id.issuer = user.issuer && cred.password = password) in
  let* user_cred = db_find authorization_server users_st search_fn in
  match user_cred with
  | None -> return (Some false)
  | Some _ -> return (Some true)