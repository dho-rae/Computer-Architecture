class Cache:
    def __init__(self):
        self.main_memory = [i % 256 for i in range(2048)]  # Initialize main memory with byte-addressable values
        self.cache = [[0] * 18 for _ in range(16)]  # Initialize cache with 16 slots and appropriate structure
        self.initialize_cache()
        self.address = None
        self.offset = None
        self.slot_number = None
        self.tag = None

    def initialize_cache(self):
        for i in range(16):
            self.cache[i][0] = 0  # Initialize valid bit to 0 for all slots
            self.cache[i][1] = 0  # Initialize tag to 0 for all slots

    def set_address(self, address):
        self.address = address

    def calculate_offset(self):
        self.offset = self.address & 0x000F

    def calculate_slot(self):
        self.slot_number = (self.address & 0x0F0) >> 4

    def calculate_tag(self):
        self.tag = self.address >> 8

    def read_cache(self):
        self.calculate_offset()
        self.calculate_slot()
        self.calculate_tag()

        if self.cache[self.slot_number][0] == 1 and self.cache[self.slot_number][1] == self.tag:
            # Cache hit
            print(f"At that byte there is the value: {self.cache[self.slot_number][2 + self.offset]:02X} (Cache Hit)")
        else:
            # Cache miss
            print("Cache Miss.")
            self.cache[self.slot_number][0] = 1  # Set valid bit
            self.cache[self.slot_number][1] = self.tag  # Set tag
            self.fetch_block_from_main_memory()
            print("Value found after fetching block from main memory:")
            print(f"{self.main_memory[self.address]:02X}")

    def fetch_block_from_main_memory(self):
        block_start_address = (self.address >> 4) << 4  # Calculate the start address of the block
        for i in range(16):
            self.cache[self.slot_number][2 + i] = self.main_memory[block_start_address + i]

    def write_cache(self, data):
        self.calculate_offset()
        self.calculate_slot()
        self.calculate_tag()

        self.cache[self.slot_number][0] = 1  # Set valid bit
        self.cache[self.slot_number][1] = self.tag  # Set tag
        self.cache[self.slot_number][2 + self.offset] = data  # Write data to cache

        # Write the modified block back to main memory (write-back policy)
        block_start_address = (self.address >> 4) << 4
        for i in range(16):
            self.main_memory[block_start_address + i] = self.cache[self.slot_number][2 + i]

        print(f"Value {data:X} has been written to address {self.address:03X}.")

    def display_cache(self):
        print("Slot Valid Tag Data")
        for i in range(16):
            valid = "{:X}".format(self.cache[i][0])  # Convert to hexadecimal without 0x prefix
            tag = "{:X}".format(self.cache[i][1])  # Convert to hexadecimal without 0x prefix
            data = ' '.join(["{:02X}".format(d) for d in self.cache[i][2:]])  # Convert to hexadecimal without 0x prefix
            print(f"{i:X}    {valid}   {tag}    {data}")


def main():
    cache = Cache()

    while True:
        operation = input("(R)ead, (W)rite, or (D)isplay Cache?\n").strip().upper()

        if operation == 'R':
            address = int(input("What address would you like read?\n"), 16)
            cache.set_address(address)
            cache.read_cache()

        elif operation == 'W':
            address = int(input("What address would you like to write to?\n"), 16)
            data = int(input("What data would you like to write at that address?\n"), 16)
            cache.set_address(address)
            cache.write_cache(data)

        elif operation == 'D':
            cache.display_cache()

        else:
            print("Invalid operation. Please choose (R)ead, (W)rite, or (D)isplay Cache.")


if __name__ == "__main__":
    main()
