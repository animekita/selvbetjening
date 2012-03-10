PRIMARY_SERVER_ADDR = 'http://localhost:8000/';

ConnectionStatus = {
    'offline' : 1,
    'primary': 2,
    'backup': 3,
}

function Server(address) {
    this.address = address;
}

Server.prototype.ping = function() {
    // TODO
}

function ConnectionManager(primary_server) {
    this.primary_server = primary_server;
    this.backup_servers = []

    this.status = ConnectionStatus.offline
}

ConnectionManager.prototype.get_status = function() {
    return this.status;
}

ConnectionManager.prototype.retry_connection = function() {

    // TODO

    if (this.status !== ConnectionStatus.primary) {
        // retry primary connection

    }
}

primary_server = Server(PRIMARY_SERVER_ADDR);

connection_manager = ConnectionManager(primary_server);