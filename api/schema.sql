create table files (
	share_id varchar(64) character set ascii,
	id char(40) character set ascii,
	path varchar(333) not null,
	name text not null,
	atime datetime not null,
	ctime datetime not null,
	mtime datetime not null,
	size bigint not null,
	updated_at datetime,
	contents longtext,
	index(path),
	primary key(share_id,id),
	fulltext key(path),
	fulltext key(name),
	fulltext key(contents)
) engine=mroonga;

create table indexing_queue (
	share_id varchar(64),
	file_id char(40),
	path text not null,
	priority boolean not null default true,
	created_at datetime not null,
	updated_at datetime,
	num_retry int not null default 0,
	primary key(share_id,file_id)
) engine=InnoDB;
