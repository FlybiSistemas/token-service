import win32serviceutil
import win32service
import wmi

def install_service(service_path, service_name):
    win32serviceutil.InstallService(
        service_path, 
        service_name, 
        service_name, 
        startType=win32service.SERVICE_AUTO_START
    )

def uninstall_service(service_path, service_name):
    #print ('Uninstalling')

def list_services():
    c = wmi.WMI()
    services = c.Win32_Service()
    services_list = []

    for service in services:
        services_list.append(service.Name)
        service_name = service.Name
        service_status = service.State

    return services_list
