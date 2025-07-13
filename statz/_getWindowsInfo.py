try:
    import wmi

    def _get_windows_specs():
        '''
        Get all of the specifications of your Windows system.\n
        It returns a list called specs. Inside the list, there are 6 items:\n
        [cpu_data, gpu_data_list, ram_data_list, storage_data_list, network_data, battery_data].

        ### Below is an index of each element in every dictionary or list.
        #### cpu_data
        {
        "name": The name of your CPU. Ex. 11th Gen Intel(R) Core(TM) i5-1135G7 @2.40GHz\n
        "manufacturer": Manufacturer of your CPU. Ex. GenuineIntel\n
        "description": Some architecture information about your CPU. Ex. Intel64 Family 6 Model 140 Stepping 1\n
        "coreCount": Core count of your CPU. Ex. 4\n
        "clockSpeed": The clock speed of your CPU in megahertz. Ex. 2419}
        #### gpu_data_list (list of dicts)
        [
        {\n
            "name": ..., "driverVersion": ..., "videoProcessor": ..., "videoModeDesc": ..., "VRAM": ...\n
        },\n
        ...\n
        ]
        #### ram_data_list (list of dicts)
        [
        {\n
            "capacity": ..., "speed": ..., "manufacturer": ..., "partNumber": ...
        },\n
        ...\n
        ]
        #### storage_data_list (list of dicts)[
        {\n
            "model": ..., "interfaceType": ..., "mediaType": ..., "size": ..., "serialNumber": ...\n
        },\n
        ...\n
        ]
        #### network_data{
        "name": The name of the network adapter. Ex. Intel(R) Wireless-AC 9462\n
        "macAddress": Your MAC Address. Ex. DC:21:48:DF:E9:68\n
        "manufacturer": Who made the device. Ex. Intel Corporation\n
        "adapterType": The type of the adapter, like Ethernet or WiFi. Ex. Ethernet 802.3\n
        "speed": The speed of the adapter in MBPS. Ex. 433.3\n}
        #### battery_data{
        "name": The model of your battery. Ex. NVMe BC711 NVMe SK hynix 256GB\n
        "estimatedChargeRemaining": How much percentage battery you have left. Ex. SCSI\n
        "batteryStatus": Status of the battery. Ex. Charging\n
        "designCapacity": The design capacity of the battery. Ex. 5000 mWh\n
        "fullChargeCapacity": The current capacity of the battery. Ex. 4950 mWh} 

        ### Notes:
        * If anything returns None, it means it could not be found.\n
        * For the GPU, RAM, Storage, and Network Adapters, it will return a list with all of your hardware of that category.\n
        '''
        # main system component
        c = wmi.WMI()

        try:
            # get cpu info
            cpu_data = {}
            for cpu in c.Win32_Processor():
                cpu_data["name"] = cpu.Name
                cpu_data["manufacturer"] = cpu.Manufacturer
                cpu_data["description"] = cpu.Description
                cpu_data["coreCount"] = cpu.NumberOfCores
                cpu_data["clockSpeed"] = cpu.MaxClockSpeed

            print("cpu info")
            print(cpu_data)
        except:
            cpu_data = None

        try:
            # get gpu info (list)
            gpu_data_list = []
            for gpu in c.Win32_VideoController():
                gpu_data = {
                    "name": gpu.Name,
                    "driverVersion": gpu.DriverVersion,
                    "videoProcessor": gpu.Description,
                    "videoModeDesc": gpu.VideoModeDescription,
                    "VRAM": int(gpu.AdapterRAM) // (1024 ** 2)
                }
                gpu_data_list.append(gpu_data)
            print("gpu info")
            print(gpu_data_list)
        except:
            gpu_data_list = None

        try:
            # get ram info (list)
            ram_data_list = []
            for ram in c.Win32_PhysicalMemory():
                ram_data = {
                    "capacity": int(ram.Capacity) // (1024 ** 2),
                    "speed": ram.Speed,
                    "manufacturer": ram.Manufacturer.strip(),
                    "partNumber": ram.PartNumber.strip()
                }
                ram_data_list.append(ram_data)
            print("ram info")
            print(ram_data_list)
        except:
            ram_data_list = None

        try:
            # get storage info (list)
            storage_data_list = []
            for disk in c.Win32_DiskDrive():
                storage_data = {
                    "model": disk.Model,
                    "interfaceType": disk.InterfaceType,
                    "mediaType": getattr(disk, "MediaType", "Unknown"),
                    "size": int(disk.Size) // (1024**3) if disk.Size else None,
                    "serialNumber": disk.SerialNumber.strip() if disk.SerialNumber else "N/A"
                }
                storage_data_list.append(storage_data)
            print("disk info")
            print(storage_data_list)
        except:
            storage_data_list = None
        
        try:
            # get network/wifi info
            network_data = {}
            for nic in c.Win32_NetworkAdapter():
                if nic.PhysicalAdapter and nic.NetEnabled:
                    network_data["name"] = nic.Name
                    network_data["macAddress"] = nic.MACAddress
                    network_data["manufacturer"] = nic.Manufacturer
                    network_data["adapterType"] = nic.AdapterType
                    network_data["speed"] = int(nic.Speed) / 1000000
            
            print("network info")
            print(network_data)
        except:
            network_data = None

        try:
            # get battery info
            battery_data = {}
            for batt in c.Win32_Battery():
                battery_data["name"] = batt.Name
                battery_data["estimatedChargeRemaining"] = batt.EstimatedChargeRemaining

                # interpret battery status
                match int(batt.BatteryStatus):
                    case 1:
                        battery_data["batteryStatus"] = "Discharging"
                    case 2:
                        battery_data["batteryStatus"] = "Plugged In, Fully Charged"
                    case 3:
                        battery_data["batteryStatus"] = "Fully Charged"
                    case 4:
                        battery_data["batteryStatus"] = "Low Battery"
                    case 5:
                        battery_data["batteryStatus"] = "Critical Battery"
                    case 6:
                        battery_data["batteryStatus"] = "Charging"
                    case 7:
                        battery_data["batteryStatus"] = "Charging (High)"
                    case 8:
                        battery_data["batteryStatus"] = "Charging (Low)"
                    case 9:
                        battery_data["batteryStatus"] = "Charging (Critical)"
                    case 10:
                        battery_data["batteryStatus"] = "Unknown"
                    case 11:
                        battery_data["batteryStatus"] = "Partially Charged"
                    case _:
                        battery_data["batteryStatus"] = "Unknown"
                    
                battery_data["designCapacity"] = getattr(batt, "DesignCapacity", "N/A")
                battery_data["fullChargeCapacity"] = getattr(batt, "FullChargeCapacity", "N/A")

            
            print("battery_info")
            print(battery_data)
        except:
            battery_data = None

        # return everything
        return cpu_data, gpu_data_list, ram_data_list, storage_data_list, network_data, battery_data
except:
    def _get_windows_specs():
        return None