'''
Send a command to the admin reminding of new signups.
'''
from django.core.management.base import BaseCommand
import os
import subprocess
from signupper.utils import get_new_signups
from mcweb.settings import MCWEB_ADMIN_EMAIL, MCWEB_ADMIN_EMAIL_URL

class Command(BaseCommand):
    ''' remind admin comman '''
    help = 'Sends an email reminder to mcweb.settings.MCWEB_ADMIN_EMAIL if there are new signups. '

    def add_arguments(self, parser):
        ''' list arguments for this command '''
        parser.add_argument('adminemail', nargs='*', type=str, help='extra email addresses to which the admin reminder is sent, in addition to the django setting MCWEB_ADMIN_EMAIL')
        
    def handle(self, *args, **options):
        ''' Command impl. '''

        signups = get_new_signups()
        
        admin_email = '''Hello admin,

There are %i new signups. Please visit %s to perform the listed admin tasks.

At the login screen, you must enter the credentials of a django super-user account, as well as the ldap password.

Please note the following:
1) To manage course subscription or other tasks for new or existing users in Moodle, please use the Moodle admin pages at https://pan-learning.org/moodle/ .
2) If you need to edit the signup instances, use the django admin tool.\n\nFull list of signup mail adresses is:\n''' % (len(signups), MCWEB_ADMIN_EMAIL_URL)

        
        # only send admin email if there are "new" signups
        if len(signups) == 0:
            return
        else:
            for signup in signups:
                admin_email = '''%s\n%s''' % (admin_email, signup.email)
                
        # parse email and addresses, and send admin email, catching errors and clearning up
        try:
            email_addrses = MCWEB_ADMIN_EMAIL
            for address in options['adminemail']:
                email_addrses = '%s %s' % (email_addrses, address)
            cmd = 'mailx -r admin@pan-learning.org -s "PaN-learning admins: new signups" %s < _admin_email' % email_addrses
            print(cmd)
            
            f = open('_admin_email', 'w') 
            f.write(admin_email)
            f.close()
            
            # this, but we need retcode
            #proc = subprocess.Popen(cmd, 
            #                        stdout=subprocess.PIPE,
            #                        stderr=subprocess.PIPE,
            #                        shell=True)
            #com = proc.communicate()
            #print('running: %s' % cmd)
            #print('std-out: %s' % com[0])
            #print('std-err: %s' % com[1])
            
            retcode = subprocess.call(cmd, shell=True)
            if retcode != 0:
                raise Exception('retcode: %s' % retcode) 
        
        except Exception as e:
            print('%s' % (e.__str__()))
        
        finally:
            os.remove('_admin_email')
