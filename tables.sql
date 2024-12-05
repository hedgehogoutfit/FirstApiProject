create table posts(
    post_id serial primary key,
    title varchar(99),
    author varchar(99),
    content varchar,
    likes int default 0,
    datetime timestamptz default date_trunc('minute', now())
);

create table comments(
    comment_id serial primary key,
    author varchar(99),
    content varchar,
    datetime timestamptz default date_trunc('minute', now()),
    post_id int references posts(post_id)
);




