CREATE TABLE emma.polls
(
 poll_id int,
 pollster varchar(36),
 start_date date,
 end_date date,
 median_date date,
 sample_size int,
 scope varchar(36),
 scope_name varchar(36),
 is_primary boolean,
 is_tpp boolean,
 party varchar(36),
 result float
);
