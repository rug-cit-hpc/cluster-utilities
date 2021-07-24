Name:		pgquota
Version:	1.2
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
* Sat Jul 24 2021 Klemen Voncina <k.voncina@rug.nl> - 1.2-1
- Updated to use with Python3 (minor version bump)
- Fixed an issue where student numbers would get cut off too far
- Changed the way terminal colors are handled internally in the script

* Wed Nov 13 2019 Klemen Voncina <k.voncina@rug.nl> - 1.1-3
- Fixed an issue where exceeding the file limit would break the script.

* Mon Aug 12 2019 Klemen Voncina <k.voncina@rug.nl> - 1.1-2
- Fixed an issue where having Python3 available would break the script.

* Mon May 27 2019 Klemen Voncina <k.voncina@rug.nl> - 1.1-1
- Better group id print.
- Printing for all of a user's groups is now optional. Default only prints for user's own group.

* Wed May 22 2019 Klemen Voncina <k.voncina@rug.nl> - 1.0-1
- Initial build

