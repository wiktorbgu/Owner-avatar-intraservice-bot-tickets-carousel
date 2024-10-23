prompt PL/SQL Developer Export User Objects for user DJANGO@SRV-OTP-NOTIFY-DB
prompt Created by viktor.chernyak on 25 Март 2024 г.
set define off
spool backup.log

prompt
prompt Creating table DESK_SERVICES
prompt ============================
prompt
@@desk_services.tab
prompt
prompt Creating table DESK_SERVICES_LOAD
prompt =================================
prompt
@@desk_services_load.tab
prompt
prompt Creating table DESK_SERVICE_USERGROUP_BINDS
prompt ===========================================
prompt
@@desk_service_usergroup_binds.tab
prompt
prompt Creating table DESK_USERGROUPS
prompt ==============================
prompt
@@desk_usergroups.tab
prompt
prompt Creating table DESK_USERGROUPS_LOAD
prompt ===================================
prompt
@@desk_usergroups_load.tab
prompt
prompt Creating table DESK_USERS
prompt =========================
prompt
@@desk_users.tab
prompt
prompt Creating table DESK_USERS_LOAD
prompt ==============================
prompt
@@desk_users_load.tab
prompt
prompt Creating table DESK_USER_GROUP_BINDS
prompt ====================================
prompt
@@desk_user_group_binds.tab
prompt
prompt Creating view DESK_USERS_ALL_INFO
prompt =================================
prompt
@@desk_users_all_info.vw
prompt
prompt Creating procedure DESK_MERGE_DATA_LOAD
prompt =======================================
prompt
@@desk_merge_data_load.prc

prompt Done
spool off
set define on
