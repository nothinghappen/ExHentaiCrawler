create table eromanga (
	id int not null auto_increment,
	gid int not null,
    token varchar(20) not null,
    archiver_key varchar(200) not null,
    title varchar(300) not null,
    title_jpn varchar(300) not null,
    category varchar(20) not null,
    thumb varchar(200) not null,
    uploader varchar(50) not null,
    posted long not null,
    filecount int not null,
    filesize long not null,
    expunged boolean not null,
    rating varchar(20) not null,
    torrentcount int not null,
    tags varchar(1000) not null,
    primary key(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

create table eroimage(
	id int not null auto_increment,
    gid int not null,
    token varchar(20) not null,
    sequence int not null,
    url varchar(100) not null,
    primary key(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

create table thumbimage(
    id int not null auto_increment,
    gid int not null,
    token varchar(20) not null,
    sequence int not null,
    url varchar(100) not null,
    primary key(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;