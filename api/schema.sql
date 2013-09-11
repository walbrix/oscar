create table files (
	id char(40) primary key,
	path varchar(333) not null,
	atime datetime not null,
	ctime datetime not null,
	mtime datetime not null,
	size bigint not null,
	updated_at datetime,
	contents text,
	index(path),
	fulltext key(path),
	fulltext key(contents)
) engine=mroonga;

create table indexing_queue (
	file_id char(40) primary key,
	path text not null,
	priority boolean not null default true,
	created_at datetime not null,
	updated_at datetime,
	num_retry int not null default 0
) engine=InnoDB;
