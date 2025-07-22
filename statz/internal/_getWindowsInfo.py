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
        # Method 1: Try MSAcpi_ThermalZoneTemperature (most common)
        try:
            c = wmi.WMI(namespace="root/wmi")
            thermal_zones = c.MSAcpi_ThermalZoneTemperature()
            if thermal_zones:
                temps = {}
                for zone in thermal_zones:
                    if hasattr(zone, 'CurrentTemperature') and zone.CurrentTemperature:
                        # Convert from tenths of Kelvin to Celsius
                        temp_celsius = (zone.CurrentTemperature / 10.0) - 273.15
                        # Only include reasonable temperature readings (0-150°C)
                        if 0 <= temp_celsius <= 150:
                            zone_name = getattr(zone, 'InstanceName', f'ThermalZone_{len(temps)}')
                            temps[zone_name] = round(temp_celsius, 1)
                if temps:
                    return temps
        except Exception as e:
            pass  # Continue to next method
        
        # Method 2: Try PowerShell with MSAcpi_ThermalZoneTemperature
        try:
            ps_script = """
            try {
                $thermal = Get-WmiObject MSAcpi_ThermalZoneTemperature -Namespace "root/wmi" -ErrorAction SilentlyContinue
                if ($thermal) {
                    $thermal | ForEach-Object {
                        if ($_.CurrentTemperature -ne $null -and $_.CurrentTemperature -gt 0) {
                            $temp = [math]::Round(($_.CurrentTemperature / 10 - 273.15), 1)
                            if ($temp -ge 0 -and $temp -le 150) {
                                $name = if ($_.InstanceName) { $_.InstanceName } else { "ThermalZone" }
                                Write-Output "$name`:$temp"
                            }
                        }
                    }
                }
            } catch { }
            """
            
            process = subprocess.Popen(['powershell.exe', '-Command', ps_script], 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE,
                                        text=True, 
                                        creationflags=subprocess.CREATE_NO_WINDOW)
            
            stdout, stderr = process.communicate(timeout=10)
            
            if process.returncode == 0 and stdout.strip():
                temps = {}
                for line in stdout.strip().split('\n'):
                    line = line.strip()
                    if ':' in line:
                        try:
                            name, temp_str = line.split(':', 1)
                            temp = float(temp_str.strip())
                            if 0 <= temp <= 150:  # Sanity check
                                temps[name.strip()] = temp
                        except (ValueError, IndexError):
                            continue
                if temps:
                    return temps
        except Exception as e:
            pass
        
        # Method 3: Try Win32_TemperatureProbe
        try:
            c = wmi.WMI()
            temp_probes = c.Win32_TemperatureProbe()
            if temp_probes:
                temps = {}
                for probe in temp_probes:
                    if hasattr(probe, 'CurrentReading') and probe.CurrentReading:
                        # Win32_TemperatureProbe readings are in tenths of Kelvin
                        temp_celsius = (probe.CurrentReading / 10.0) - 273.15
                        if 0 <= temp_celsius <= 150:
                            probe_name = getattr(probe, 'Name', f'TemperatureProbe_{len(temps)}') or f'TemperatureProbe_{len(temps)}'
                            temps[probe_name] = round(temp_celsius, 1)
                if temps:
                    return temps
        except Exception as e:
            pass
        
        # Method 4: Try OpenHardwareMonitor namespace (if installed)
        try:
            c = wmi.WMI(namespace="root/OpenHardwareMonitor")
            sensors = c.Sensor()
            temps = {}
            for sensor in sensors:
                if (hasattr(sensor, 'SensorType') and sensor.SensorType == 'Temperature' and
                    hasattr(sensor, 'Value') and sensor.Value is not None):
                    temp = float(sensor.Value)
                    if 0 <= temp <= 150:
                        sensor_name = getattr(sensor, 'Name', f'Sensor_{len(temps)}') or f'Sensor_{len(temps)}'
                        temps[sensor_name] = round(temp, 1)
            if temps:
                return temps
        except Exception as e:
            pass
        
        # Method 5: Try LibreHardwareMonitor namespace (if installed)
        try:
            c = wmi.WMI(namespace="root/LibreHardwareMonitor")
            sensors = c.Sensor()
            temps = {}
            for sensor in sensors:
                if (hasattr(sensor, 'SensorType') and sensor.SensorType == 'Temperature' and
                    hasattr(sensor, 'Value') and sensor.Value is not None):
                    temp = float(sensor.Value)
                    if 0 <= temp <= 150:
                        sensor_name = getattr(sensor, 'Name', f'Sensor_{len(temps)}') or f'Sensor_{len(temps)}'
                        temps[sensor_name] = round(temp, 1)
            if temps:
                return temps
        except Exception as e:
            pass
        
        # Method 6: Fallback - try to get CPU package temperature via PowerShell and typeperf
        try:
            ps_script = """
            try {
                $counter = "\\Thermal Zone Information(_Total)\\Temperature"
                $sample = Get-Counter $counter -MaxSamples 1 -ErrorAction SilentlyContinue
                if ($sample -and $sample.CounterSamples) {
                    $temp = $sample.CounterSamples[0].CookedValue
                    if ($temp -gt 0) {
                        $temp_celsius = [math]::Round(($temp - 273.15), 1)
                        if ($temp_celsius -ge 0 -and $temp_celsius -le 150) {
                            Write-Output "System_Temperature:$temp_celsius"
                        }
                    }
                }
            } catch { }
            """
            
            process = subprocess.Popen(['powershell.exe', '-Command', ps_script], 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE,
                                        text=True, 
                                        creationflags=subprocess.CREATE_NO_WINDOW)
            
            stdout, stderr = process.communicate(timeout=10)
            
            if process.returncode == 0 and stdout.strip():
                for line in stdout.strip().split('\n'):
                    line = line.strip()
                    if ':' in line:
                        try:
                            name, temp_str = line.split(':', 1)
                            temp = float(temp_str.strip())
                            if 0 <= temp <= 150:
                                return {name.strip(): temp}
                        except (ValueError, IndexError):
                            continue
        except Exception as e:
            pass
        
        # If all methods fail, return a helpful message instead of None
        return {"error": "Temperature sensors not available or accessible on this Windows system"}

except:
    def _get_windows_specs():
        return None, None, None, None, None, None, None

    def _get_windows_temps():
        return None