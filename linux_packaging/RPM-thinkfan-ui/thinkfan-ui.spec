# RPM Spec file for thinkfan-ui
# This file is used by rpmbuild to create the RPM package.

Name:       thinkfan-ui
Version:    1.0.0
Release:    1%{?dist}
Summary:    A GUI for controlling fan speed on ThinkPads

License:    GPL-3.0-only
URL:        https://github.com/zocker-160/thinkfan-ui
Source0:    %{name}-%{version}.tar.gz

BuildArch:  noarch

Requires:   python3
Requires:   python3-pyqt6
Requires:   python3-pyyaml
Requires:   lm_sensors
Requires:   polkit

%description
A small GUI application for Linux to control the fan speed and monitor temperatures on IBM/Lenovo ThinkPads. It provides a simple interface to set fan levels and view sensor data.

%prep
%setup -q

%build
# Nothing to build for a Python application

%install
rm -rf %{buildroot}

# --- Install application files to /opt/thinkfan-ui ---
install -d -m755 %{buildroot}/opt/%{name}
# Use RPM macros for a robust path to the source files
cp -a %{_builddir}/%{name}-%{version}/src/. %{buildroot}/opt/%{name}/

# --- Install launcher script ---
install -d -m755 %{buildroot}%{_bindir}
install -m755 %{_builddir}/%{name}-%{version}/linux_packaging/thinkfan-ui %{buildroot}%{_bindir}/%{name}

# --- Install desktop and icon files ---
install -d -m755 %{buildroot}%{_datadir}/applications
install -m644 %{_builddir}/%{name}-%{version}/linux_packaging/thinkfan-ui.desktop %{buildroot}%{_datadir}/applications/

install -d -m755 %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
install -m644 %{_builddir}/%{name}-%{version}/linux_packaging/thinkfan-ui.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg

# --- Install kernel module configuration ---
install -d -m755 %{buildroot}/usr/lib/modules-load.d
install -m644 %{_builddir}/%{name}-%{version}/linux_packaging/modules-load.conf %{buildroot}/usr/lib/modules-load.d/%{name}.conf

%pre
# This script runs before the package is installed.
if ! grep -q -r -F "options thinkpad_acpi fan_control=1" /etc/modprobe.d/; then
    echo "options thinkpad_acpi fan_control=1" > /etc/modprobe.d/thinkpad_acpi.conf
fi
modprobe -r thinkpad_acpi || true
modprobe thinkpad_acpi

%postun
# This script runs after the package is uninstalled.
find /opt/%{name} -type f -iname \*.pyc -delete
find /opt/%{name} -type d -iname __pycache__ -delete
# If our config file is the only one left, remove it
if [ -f /etc/modprobe.d/thinkpad_acpi.conf ] && [ $(grep -r -F "options thinkpad_acpi fan_control=1" /etc/modprobe.d/ | wc -l) -eq 1 ]; then
    rm /etc/modprobe.d/thinkpad_acpi.conf
fi


%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
/opt/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg
/usr/lib/modules-load.d/%{name}.conf

%changelog
* Thu Aug 01 2025 zocker_160 <zocker1600@posteo.net> - 1.0.0-1
- PyQt6 port and UI upgrade
* Thu Aug 01 2024 Your Name <your.email@example.com> - 0.11.0-5
- Use absolute RPM macros for file paths to ensure build reliability
* Thu Aug 01 2024 Your Name <your.email@example.com> - 0.11.0-4
- Replaced non-portable pushd with robust cp command
* Thu Aug 01 2024 Your Name <your.email@example.com> - 0.11.0-3
- Fixed file copy issue during RPM install phase
* Thu Aug 01 2024 Your Name <your.email@example.com> - 0.11.0-2
- Corrected installation path to /opt/thinkfan-ui
* Wed Jul 31 2024 Your Name <your.email@example.com> - 0.11.0-1
- Initial RPM packaging
