create or replace view desk_users_all_info as
select t.id,
       case when t.id = s.last_user_id then '<=' end as last_user,
       t.enabled,
       t.name,
       t.off_start_date,
       t.off_end_date,
       t.email,
       s.enabled enabled_service,
       s.id service_id,
       s.name service_name,
       g.id usergroup_id,
       g.name usergroup_name
       from DESK_USERS t
join DESK_USER_GROUP_BINDS a on t.id = a.userid
join DESK_USERGROUPS g on g.id = a.usergroupid
join Desk_Service_Usergroup_Binds sb on sb.usergroup_id = g.id
join DESK_SERVICES s on s.id = sb.service_id;

