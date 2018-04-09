from network import Bluetooth
import binascii

class BluetoothServer:

    char1 = 0

    message = ""

    def set_message(self, message):
        self.char1.value(message)

    def conn_cb (self, bt_o):
        events = bt_o.events()
        if  events & Bluetooth.CLIENT_CONNECTED:
            print("Client connected")
            print("char1 value: {}".format(self.char1.value()))
            self.char1.value(2)
            print("char1 value: {}".format(self.char1.value()))
        elif events & Bluetooth.CLIENT_DISCONNECTED:
            print("Client disconnected")

    def char1_cb_handler(self, chr):

        events = chr.events()
        if  events & Bluetooth.CHAR_WRITE_EVENT:
            print("Write request with value = {}".format(chr.value()))
        elif events:
            return "message: {}".format(self.message);

    def uuid2bytes(self, uuid):
        uuid = uuid.encode().replace(b'-',b'')
        tmp = binascii.unhexlify(uuid)
        return bytes(reversed(tmp))

    char1_read_counter = 0
    def run(self):
        bluetooth = Bluetooth()
        bluetooth.set_advertisement(name='LoPy', service_uuid=b'1234567890123456')

        bluetooth.callback(trigger=Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED, handler=self.conn_cb)
        bluetooth.advertise(True)

        #Create a new service on the internal GATT server. Returns a object of type BluetoothServerService.
        srv1 = bluetooth.service(uuid=self.uuid2bytes('00001819-0000-1000-8000-00805f9b34fb'), isprimary=True)

        #Creates a new characteristic on the service. Returns an object of the class GATTSCharacteristic
        self.char1 = srv1.characteristic(uuid=self.uuid2bytes('00002a67-0000-1000-8000-00805f9b34fb'), properties=Bluetooth.PROP_BROADCAST | Bluetooth.PROP_INDICATE, value = 1)

        #Creates a callback that will be executed when any of the triggers occurs
        char1_cb = self.char1.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=self.char1_cb_handler)
