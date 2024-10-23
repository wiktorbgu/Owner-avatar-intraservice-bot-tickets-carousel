ACTIVE_SERVICES = '''SELECT T.ID
  FROM DESK_SERVICES T
 WHERE T.ENABLED = 1
 ORDER BY T.ID'''

ACTIVE_SERVICE_USERS = '''select t.id,
       t.name,
       s.last_user_id
       from DESK_USERS t
join DESK_USER_GROUP_BINDS a on t.id = a.userid
join DESK_USERGROUPS g on g.id = a.usergroupid
join Desk_Service_Usergroup_Binds sb on sb.usergroup_id = g.id
join DESK_SERVICES s on s.id = sb.service_id
where t.enabled = 1
and sb.service_id = :service_id
and ((trunc(sysdate) < t.off_start_date or trunc(sysdate) > t.off_end_date) or (t.off_start_date is null or t.off_end_date is null))
order by t.id'''

SET_LAST_USER_SERVICE = 'update DESK_SERVICES t set t.last_user_id = :last_user_id where t.id = :service_id'
