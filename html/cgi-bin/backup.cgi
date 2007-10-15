#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007  Michael Tremer & Christian Schmidt                      #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

use strict;
# enable only the following on debugging purpose
use warnings;
use CGI::Carp 'fatalsToBrowser';
use File::Copy;

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %color = ();
my %mainsettings = ();
my %cgiparams=();
my %checked = ();
my $message = "";
my $errormessage = "";

$a = new CGI;

&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/".$mainsettings{'THEME'}."/include/colors.txt", \%color);

$cgiparams{'ACTION'} = '';
$cgiparams{'FILE'} = '';
$cgiparams{'UPLOAD'} = '';
$cgiparams{'BACKUPLOGS'} = '';

&Header::getcgihash(\%cgiparams);

############################################################################################################################
############################################## System calls ohne Http Header ###############################################


if ( $cgiparams{'ACTION'} eq "download" )
{
		open(DLFILE, "</var/ipfire/backup/$cgiparams{'FILE'}") or die "Unable to open $cgiparams{'FILE'}: $!";
		my @fileholder = <DLFILE>;
		print "Content-Type:application/x-download\n";
		print "Content-Disposition:attachment;filename=$cgiparams{'FILE'}\n\n";
		print @fileholder;
		exit (0);
}
elsif ( $cgiparams{'ACTION'} eq "restore" )
{
		my $upload = $a->param("UPLOAD");
		open UPLOADFILE, ">/tmp/restore.ipf";
		binmode $upload;
		while ( <$upload> ) {
		print UPLOADFILE;
		}
		close UPLOADFILE;
		system("/usr/local/bin/backupctrl restore >/dev/null 2>&1");
}

&Header::showhttpheaders();

sub refreshpage{&Header::openbox( 'Waiting', 1, "<meta http-equiv='refresh' content='1;'>" );print "<center><img src='/images/clock.gif' alt='' /><br/><font color='red'>$Lang::tr{'pagerefresh'}</font></center>";&Header::closebox();}

&Header::openpage($Lang::tr{'backup'}, 1, "");
&Header::openbigbox('100%', 'left', '', $errormessage);

############################################################################################################################
################################################### Default System calls ###################################################

if ( $cgiparams{'ACTION'} eq "backup" )
{
	if ( $cgiparams{'BACKUPLOGS'} eq "include" ){system("/usr/local/bin/backupctrl include >/dev/null 2>&1");}
	else {system("/usr/local/bin/backupctrl exclude >/dev/null 2>&1");}
}
if ( $cgiparams{'ACTION'} eq "addonbackup" )
{
	system("/usr/local/bin/backupctrl addonbackup $cgiparams{'ADDON'}");
}
elsif ( $cgiparams{'ACTION'} eq "delete" )
{
	system("/usr/local/bin/backupctrl $cgiparams{'FILE'} >/dev/null 2>&1");
}

############################################################################################################################
############################################ Backups des Systems erstellen #################################################

if ( $message ne "" ){
	&Header::openbox('100%','left',$Lang::tr{'error messages'});
	print "<font color='red'>$message</font>\n";
	&Header::closebox();
}

my @backups = `cd /var/ipfire/backup/ && ls *.ipf 2>/dev/null`;

&Header::openbox('100%', 'center', $Lang::tr{'backup'});

print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='95%' cellspacing='0'>
<tr><td align='left' width='40%'>$Lang::tr{'logs'}</td><td align='left'>include Logfiles
	<input type='radio' name='BACKUPLOGS' value='include'/>/
	<input type='radio' name='BACKUPLOGS' value='exclude' checked='checked'/> exclude Logfiles
</td></tr>
<tr><td align='center' colspan='2'>
	<input type='hidden' name='ACTION' value='backup' />
	<input type='image' alt='$Lang::tr{'backup'}' title='$Lang::tr{'backup'}' src='/images/document-save.png' />
</td></tr>
</table>
</form>
END
;
&Header::closebox();

############################################################################################################################
############################################ Backups des Systems downloaden ################################################

&Header::openbox('100%', 'center', $Lang::tr{'backups'});

print <<END
<table width='95%' cellspacing='0'>
END
;
foreach (@backups){
chomp($_);
my $Datei = "/var/ipfire/backup/".$_;
my @Info = stat($Datei);
my $Size = $Info[7] / 1024;
$Size = sprintf("%02d", $Size);
print "<tr><td align='center'>$Lang::tr{'backup from'} $_ $Lang::tr{'size'} $Size KB</td><td width='5'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='ACTION' value='download' /><input type='hidden' name='FILE' value='$_' /><input type='image' alt='$Lang::tr{'download'}' title='$Lang::tr{'download'}' src='/images/package-x-generic.png' /></form></td>";
print "<td width='5'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='hidden' name='ACTION' value='delete' /><input type='hidden' name='FILE' value='$_' /><input type='image' alt='$Lang::tr{'delete'}' title='$Lang::tr{'delete'}' src='/images/user-trash.png' /></form></td></tr>";
}
print <<END
</table>
END
;
&Header::closebox();

############################################################################################################################
####################################### Backups des Systems wiederherstellen ###############################################

&Header::openbox('100%', 'center', $Lang::tr{'restore'});

print <<END
<table width='95%' cellspacing='0'>
<tr><td align='left'>$Lang::tr{'backup'}</td><td align='left'><form method='post' enctype='multipart/form-data' action='$ENV{'SCRIPT_NAME'}'><input type="file" size='50' name="UPLOAD" /><input type='hidden' name='ACTION' value='restore' /><input type='hidden' name='FILE' value='$_' /><input type='image' alt='$Lang::tr{'restore'}' title='$Lang::tr{'restore'}' src='/images/media-floppy.png' /></form></td></tr>
</table>
END
;
&Header::closebox();

############################################################################################################################
############################################# Backups von Addons erstellen #################################################

&Header::openbox('100%', 'center', 'addons');

my @addonincluds = `ls /var/ipfire/backup/addons/includes/ 2>/dev/null`;

print "<table width='95%' cellspacing='0'>";
foreach (@addonincluds){
chomp($_);
my $Datei = "/var/ipfire/backup/addons/backup/".$_.".ipf";
my @Info = stat($Datei);
my $Size = $Info[7] / 1024;
$Size = sprintf("%2d", $Size);
if ( -e $Datei ){
print "<tr><td align='center'>$Lang::tr{'backup from'} $_ $Lang::tr{'size'} $Size KB $Lang::tr{'date'} ".localtime($Info[9])."</td>";
print <<END
	<td align='right' width='5'>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<input type='hidden' name='ACTION' value='download' />
		<input type='hidden' name='FILE' value='addons/backup/$_.ipf' />
		<input type='image' alt='$Lang::tr{'download'}' title='$Lang::tr{'download'}' src='/images/package-x-generic.png' />
		</form>
	</td>
	<td align='right' width='5'>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<input type='hidden' name='ACTION' value='delete' />
		<input type='hidden' name='FILE' value='addons/backup/$_.ipf' />
		<input type='image' alt='$Lang::tr{'delete'}' title='$Lang::tr{'delete'}' src='/images/user-trash.png' />
		</form>
	</td>
END
;
}
else{
  print "<tr><td align='center'>$Lang::tr{'backup from'} $_ </td><td colspan='2' width='10'></td>";
}
print <<END
	<td align='right' width='5'>
		<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<input type='hidden' name='ACTION' value='addonbackup' />
		<input type='hidden' name='ADDON' value='$_' />
		<input type='image' alt='$Lang::tr{'backup'}' title='$Lang::tr{'backup'}' src='/images/document-save.png' />
		</form>
	</td></tr>
END
;
}
print "</table>";
&Header::closebox();
&Header::closebigbox();
&Header::closepage();
