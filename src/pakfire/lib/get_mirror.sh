############################################################################################
# Version 0.1a, Copyright (C) 2006  by IPFire.org						  #
# IPFire ist freie Software, die Sie unter bestimmten Bedingungen weitergeben d�rfen.      #
############################################################################################

get_mirror() {

cd $PAKHOME/cache

if [ -e $PAKHOME/cache/$SERVERS_LIST ]
 then rm -f $PAKHOME/cache/$SERVERS_LIST
fi

if /usr/bin/wget -q $H_MIRROR >/dev/null 2>&1
 then
  cd -
  return 0
 else
  cd -
  return 1
fi

}
################################### EOF ####################################################
