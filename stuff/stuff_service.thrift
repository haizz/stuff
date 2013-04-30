struct Item {
	1: binary key,
	2: i64 timestamp,
	4: binary data
}

exception NotFoundException
{
	1: string msg
}

service StuffStorage {
	void ping(),
	void put(1: Item item),
	Item get(1: binary key) throws (1:NotFoundException ex),
	oneway void meet_neighbor(1: string address),
	oneway void sync_put(1: Item item, 2: list<string> propagation_trace),
	list<Item> sync_get(1: i64 latest_timestamp)
}
