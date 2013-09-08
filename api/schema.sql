create table file (
	id char(40) primary key,
	path text not null,
	atime datetime not null,
	ctime datetime not null,
	mtime datetime not null,
	updated_at datetime,
	contents text,
	fulltext key(path),
	fulltext key(contents)
) engine=MyISAM;

create table indexing_queue (
	file_id char(40) primary key,
	path text not null,
	created_at datetime not null,
	updated_at datetime,
	num_retry int not null default 0
) engine=InnoDB;
