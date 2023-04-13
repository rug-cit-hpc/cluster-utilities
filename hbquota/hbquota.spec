Name:      hbquota
Version:   2.0
Release:   1%{?dist}
Summary:   Shows user file and data quotas per Hábrók file system

Group:     System Environment/Base
License:   MIT
URL:       https://github.com/rug-cit-hpc/cluster-utilities
Source0:   %{name}-%{version}.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
Requires:  python3


%description
hbquota - shows user's quota for all Hábrók file systems, and presents this information in a nicely readable format.

%prep
%setup -q

%build

%install
mkdir -p $RPM_BUILD_ROOT/usr/bin
install hbquota/hbquota $RPM_BUILD_ROOT/usr/bin/hbquota

%files

#%doc

/usr/bin/hbquota

%clean
rm -rf $RPM_BUILD_ROOT

%changelog
* Thu Apr 13 2023 Fokke Dijkstra <f.dijkstra@rug.nl> - 2.0-1
- Updated pgquota to work as hbquota on the new Hábrók cluster
* Wed Apr 13 2022 Fokke Dijkstra <f.dijkstra@rug.nl> - 1.3-2
- Fixed a regression where the * was no longer removed from
  out of quota numbers reported by Lustre.
* Wed Jan 12 2022 Fokke Dijkstra <f.dijkstra@rug.nl> - 1.3-1
- Adjusted pgquota to be able to work on a NFS exported
  ZFS file system. Since ZFS does not export the quota
  through NFS The quota must be dumped into a file on
  the file system in a cron job.

* Mon Sep 20 2021 Klemen Voncina <k.voncina@rug.nl> - 1.2-1
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

