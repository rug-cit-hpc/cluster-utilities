Name:		pgquota
Version:	1.0
Release:	1%{?dist}
Summary:	Shows lfs user file and data quotas per file system

Group:		System Environment/Base
License:	MIT
URL:		https://github.com/rug-cit-hpc/cluster-utilities
Source0:	%{name}-%{version}.tar.gz
BuildArch:	noarch
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root
Requires:	python


%description
pgquota - uses lfs to check a user's quota for all file systems then presents this information in a nicely readable format.

%prep
%setup -q

%build

%install
mkdir -p $RPM_BUILD_ROOT/usr/bin
install pgquota $RPM_BUILD_ROOT/usr/bin/pgquota

%files

#%doc

/usr/bin/pgquota

%clean
rm -rf $RPM_BUILD_ROOT

%changelog
* Wed May 22 2019 Klemen Voncina <k.voncina@rug.nl> - 1.0-1
- Initial build

