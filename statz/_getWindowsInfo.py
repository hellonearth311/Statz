import subprocess
try:
    import wmi

    def _get_windows_specs(get_os, get_cpu, get_gpu, get_ram, get_disk, get_network, get_battery):
        """
        Get all of the specifications of your Windows system with selective fetching.

        This function allows you to specify which components to fetch data for, improving performance by avoiding unnecessary computations.

        Args:
            get_os (bool): Whether to fetch OS specs.
            get_cpu (bool): Whether to fetch CPU specs.
            get_gpu (bool): Whether to fetch GPU specs.
            get_ram (bool): Whether to fetch RAM specs.
            get_disk (bool): Whether to fetch disk specs.
            get_network (bool): Whether to fetch network specs.
            get_battery (bool): Whether to fetch battery specs.

        Returns:
            list: A list containing specs data for the specified components:
            [os_data (dict), cpu_data (dict), gpu_data_list (list of dicts), ram_data_list (list of dicts),
            storage_data_list (list of dicts), network_data (dict), battery_data (dict)].

        Raises:
            Exception: If fetching data for a specific component fails.

        Note:
            - Components not requested will return None in the corresponding list position.
            - GPU, network, and battery specs are only available on Windows.
        """
        specs = []

        # Initialize WMI client
        c = wmi.WMI()

        # os info
        if get_os:
            try:
                os_data = {}
                for os in c.Win32_OperatingSystem():
                    os_data["system"] = os.Name.split('|')[0].strip()
                    os_data["version"] = os.Version
                    os_data["buildNumber"] = os.BuildNumber
                    os_data["servicePackMajorVersion"] = os.ServicePackMajorVersion
                    os_data["architecture"] = os.OSArchitecture
                    os_data["manufacturer"] = os.Manufacturer
                    os_data["serialNumber"] = os.SerialNumber
                    break
            except:
                os_data = None
            specs.append(os_data)
        else:
            specs.append(None)

        # cpu info
        if get_cpu:
            try:
                cpu_data = {}
                for cpu in c.Win32_Processor():
                    cpu_data["name"] = cpu.Name
                    cpu_data["manufacturer"] = cpu.Manufacturer
                    cpu_data["description"] = cpu.Description
                    cpu_data["coreCount"] = cpu.NumberOfCores
                    cpu_data["clockSpeed"] = cpu.MaxClockSpeed
            except:
                cpu_data = None
            specs.append(cpu_data)
        else:
            specs.append(None)

        # gpu info
        if get_gpu:
            try:
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
            except:
                gpu_data_list = None
            specs.append(gpu_data_list)
        else:
            specs.append(None)

        # ram info
        if get_ram:
            try:
                ram_data_list = []
                for ram in c.Win32_PhysicalMemory():
                    ram_data = {
                        "capacity": int(ram.Capacity) // (1024 ** 2),
                        "speed": ram.Speed,
                        "manufacturer": ram.Manufacturer.strip(),
                        "partNumber": ram.PartNumber.strip()
                    }
                    ram_data_list.append(ram_data)
            except:
                ram_data_list = None
            specs.append(ram_data_list)
        else:
            specs.append(None)

        # disk info
        if get_disk:
            try:
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
            except:
                storage_data_list = None
            specs.append(storage_data_list)
        else:
            specs.append(None)

        # network info
        if get_network:
            try:
                network_data = {}
                for nic in c.Win32_NetworkAdapter():
                    if nic.PhysicalAdapter and nic.NetEnabled:
                        network_data["name"] = nic.Name
                        network_data["macAddress"] = nic.MACAddress
                        network_data["manufacturer"] = nic.Manufacturer
                        network_data["adapterType"] = nic.AdapterType
                        network_data["speed"] = int(nic.Speed) / 1000000
            except:
                network_data = None
            specs.append(network_data)
        else:
            specs.append(None)

        # battery info
        if get_battery:
            try:
                battery_data = {}
                for batt in c.Win32_Battery():
                    battery_data["name"] = batt.Name
                    battery_data["estimatedChargeRemaining"] = batt.EstimatedChargeRemaining
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
            except:
                battery_data = None
            specs.append(battery_data)
        else:
            specs.append(None)

        return specs
    
    def _get_windows_temps():
        """
        Get Windows temperature using multiple methods for better compatibility
        """
        try:
            ps_script = """
            $t = Get-WmiObject MSAcpi_ThermalZoneTemperature -Namespace "root/wmi"
            if ($t) {
                $t | ForEach-Object {
                    $temp = $_.CurrentTemperature / 10 - 273.15
                    Write-Host "ThermalZone $($_.InstanceName): $temp"
                }
            }
            """
            
            process = subprocess.Popen(['powershell.exe', '-Command', ps_script], 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE,
                                        text=True, 
                                        creationflags=subprocess.CREATE_NO_WINDOW)
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0 and stdout.strip():
                temps = {}
                for line in stdout.strip().split('\n'):
                    if 'ThermalZone' in line and ':' in line:
                        try:
                            parts = line.split(': ')
                            if len(parts) == 2:
                                zone_name = parts[0].strip()
                                temp = float(parts[1].strip())
                                temps[zone_name] = temp
                        except:
                            continue
                if temps:
                    return temps
        except:
            pass
        
        try:
            ps_script = """
            $probes = Get-WmiObject -Class Win32_TemperatureProbe
            if ($probes) {
                $probes | ForEach-Object {
                    if ($_.CurrentReading -ne $null) {
                        $temp = $_.CurrentReading / 10 - 273.15
                        Write-Host "TempProbe $($_.Name): $temp"
                    }
                }
            }
            """
            
            process = subprocess.Popen(['powershell.exe', '-Command', ps_script], 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE,
                                        text=True, 
                                        creationflags=subprocess.CREATE_NO_WINDOW)
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0 and stdout.strip():
                temps = {}
                for line in stdout.strip().split('\n'):
                    if 'TempProbe' in line and ':' in line:
                        try:
                            parts = line.split(': ')
                            if len(parts) == 2:
                                probe_name = parts[0].strip()
                                temp = float(parts[1].strip())
                                temps[probe_name] = temp
                        except:
                            continue
                if temps:
                    return temps
        except:
            pass
        
        try:
            ps_script = """
            $sensors = Get-WmiObject -Namespace "root/OpenHardwareMonitor" -Class Sensor | Where-Object { $_.SensorType -eq "Temperature" }
            if ($sensors) {
                $sensors | ForEach-Object {
                    Write-Host "$($_.Name): $($_.Value)"
                }
            }
            """
            
            process = subprocess.Popen(['powershell.exe', '-Command', ps_script], 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE,
                                        text=True, 
                                        creationflags=subprocess.CREATE_NO_WINDOW)
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0 and stdout.strip():
                temps = {}
                for line in stdout.strip().split('\n'):
                    if ':' in line:
                        try:
                            parts = line.split(': ')
                            if len(parts) == 2:
                                sensor_name = parts[0].strip()
                                temp = float(parts[1].strip())
                                temps[sensor_name] = temp
                        except:
                            continue
                if temps:
                    return temps
        except:
            pass
        
        try:
            ps_script = """
            $thermal = Get-WmiObject -Query "SELECT * FROM Win32_PerfRawData_Counters_ThermalZoneInformation"
            if ($thermal) {
                $thermal | ForEach-Object {
                    if ($_.Temperature -ne $null) {
                        $temp = $_.Temperature / 10 - 273.15
                        Write-Host "Thermal: $temp"
                    }
                }
            }
            """
            
            process = subprocess.Popen(['powershell.exe', '-Command', ps_script], 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE,
                                        text=True, 
                                        creationflags=subprocess.CREATE_NO_WINDOW)
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0 and stdout.strip():
                for line in stdout.strip().split('\n'):
                    if 'Thermal:' in line:
                        try:
                            temp = float(line.split(': ')[1].strip())
                            return {'thermal': temp}
                        except:
                            continue
        except:
            pass
        
        return None

except:
    def _get_windows_specs():
        return None, None, None, None, None, None, None

    def _get_windows_temps():
        return None