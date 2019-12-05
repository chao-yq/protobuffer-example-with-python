protoc  -I=simple --python_out=simple\ simple\*.proto
protoc -I=addressbook --python_out=addressbook\  addressbook\*.proto
protoc  --python_out=pdcpDaemon\ pdcpDaemon\*.proto