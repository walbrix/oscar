create table files (
	share_id varchar(128) character set utf8,
	id char(40) character set ascii,
	path varchar(333) not null,
	path_ft text not null,
	name text not null,
	atime datetime not null,
	ctime datetime not null,
	mtime datetime not null,
	size bigint not null,
	updated_at datetime,
	contents longtext,
	sha1sum char(40) character set ascii default 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
	primary key(share_id,id),
	index(path),
	index(sha1sum),
	fulltext key(path_ft) COMMENT 'parser "TokenBigramSplitSymbolAlphaDigit"',
	fulltext key(name) COMMENT 'parser "TokenBigramSplitSymbolAlphaDigit"',
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

create table system_settings (
	name varchar(64) primary key,
	value text
) engine=MyISAM;
