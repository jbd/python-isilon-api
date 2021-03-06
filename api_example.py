#API Usage Example
#==========
#To use: Modify the fqdn, username, and password
# Create a directory called /ifs/data/test on your cluster
import isilon
import time
import logging

def main():
	fqdn = '192.168.167.101'  #change to your cluster
	username = 'root'
	password = 'a'
	testfolder = '/ifs/apitest_' + str(int(time.time()))
	
	#httplib.HTTPConnection.debuglevel = 1
	logging.basicConfig()  
	logging.getLogger().setLevel(logging.CRITICAL)
	logging.captureWarnings(True)


	#connect, secure=False allows us to bypass the CA validation
	api = isilon.API(fqdn, username, password, secure=False)

	# not necessary as it will connect automatically on auth failure
	# but this avoids the initial attempt failure
	print("Connecting")
	api.session.connect()
	
	#Create some test files / folders
	print("Creating test folders and files")
	api.namespace.dir_create(testfolder)
	for x in ('a','b','c'):
		subfolder = testfolder + '/' + x
		api.namespace.dir_create(subfolder)
		for y in range(1,10):
			api.namespace.file_create(subfolder + '/' + str(x) + str(y),"test_file")
		
		
	#Check for old bad snaps and delete
	#Get info for testsnap, will throw exception if not found
	print("Checking for older snaps")	
	
	if api.platform.snapshot('testsnap') :
		api.session.debug_last()
		print("We found an existing testsnap, let's delete that...")
		api.platform.snapshot_delete('testsnap')
	
	 	
	#This shows how we can pass params directly to the API though specifically not called
	#out as a param for the snapshot_create function.  	
	print("create a snapshot on %s, to expire in 60 seconds" % testfolder )
	api.platform.snapshot_create("testsnap",testfolder,expires=int(time.time()+60))
	
	print("confirm test snapshot was created details:")
	print(api.platform.snapshot('testsnap'))

	print("Modify the snapshot expire time and rename to testsnap2")
	api.platform.snapshot_modify('testsnap',name='testsnap2',expires=int(time.time() + 120))
	print("Rename back testsnap")
	api.platform.snapshot_modify('testsnap2',name='testsnap')

	#Error handling examples
	logging.getLogger().setLevel(logging.CRITICAL)
	try:		
		api.platform.snapshot_create('testsnap','/junkjunkifs/data/test')
	except isilon.APIError, e:
		print("Snapshot Creation error caught succesfully")
	
	#Try to delete all snaps, we intentionally block an empty name field on delete
	#As that will delete all snaps, we've create a separate function that allows that
	print("Using a command in an invalid way to show excption catchign")
	try:
		api.platform.snapshot_delete('')
	except isilon.IsilonLibraryError:
		#use snapshot_delete_all() instead
		print("invalid fucntion use caught correctly")
	logging.getLogger().setLevel(logging.ERROR)

	#list all snaps
	print('\nListing of All Snaps:')
	for snap in api.platform.snapshot(limit=2):
		print("Name: %s, Path: %s, Created: %s" % (snap['name'], snap['path'], time.ctime(snap['created']) ))

	#cleanup our testnsap
	api.platform.snapshot_delete('testsnap')

	#namespace example
	dir_a = []
	dir_b = []
	print("Is %s a dir? %s" % ( testfolder , api.namespace.is_dir(testfolder)))
	
	gena = api.namespace.dir(testfolder + '/a', limit=2, sort='name', dir='ASC')
	genb = api.namespace.dir(testfolder + '/b', limit=2, sort='name',dir='DESC')
	while True:
		try:
			itema = gena.next()
			itemb = genb.next()
			dir_a.append(itema['name'])
			dir_b.append(itemb['name'])
		except StopIteration:
			break			
	print("Listing for %s , Asecending" % testfolder + '/a')
	print("dir_a: %s" % str(dir_a))
	print("Listing for %s , Descending" % testfolder + '/b')
	print("dir_b: %s" % str(dir_b))
	
	print("list all quotas")
	for q in api.platform.quota():
		pcnt_used = 100 * q['usage']['logical'] / q['thresholds']['hard']
		print("Path %s  Persona: %s   Percent Used: %s" % (q['path'] , q['persona'], pcnt_used))
	
			
			
		 
if __name__ == "__main__":
    main()