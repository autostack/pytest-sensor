%define name pytest_sensor
%define version $VERSION

Summary: Plugin for py.test to track real time tests
Name: %{name}
Version: %{version}
Release: 1%{?dist}
Source0: %{name}-%{version}.tar.gz
License: MIT
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Avi Tal <avi3tal@gmail.com>
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}

# RHEL > 5
%if 0%{?rhel} && 0%{?rhel} > 5
BuildRequires: python2-devel
%endif

# FEDORA > 17
%if 0%{?fedora} >= 18
BuildRequires: python-devel
%endif

BuildRequires: python-setuptools
BuildRequires: python-pbr
Requires: sshpass
Requires: redis
Requires: PyYAML
Requires: python-ansible
Requires: python-pytest
Requires: python-redis
Requires: python-six


%description
# pytest-ansible
Advanced pytest plugin for monitoring capabilities
.


%prep
%setup -n %{name}-%{version} -n %{name}-%{version}

%build
python setup.py build

%install
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES


%clean
rm -rf $RPM_BUILD_ROOT

%post
systemctl start redis.service
systemctl enable redis.service

%files -f INSTALLED_FILES
%defattr(-,root,root)
