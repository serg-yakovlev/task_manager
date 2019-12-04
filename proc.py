import psutil

processes = []
for proc in psutil.process_iter():
	processes.append({
		'proc': proc, 
		'mem': proc.memory_info(), 
		'info': proc.as_dict(), 
		'id': proc.pid
		})

processes.sort(key=lambda x: x['info']['memory_percent'], reverse=True)

for proc in processes[:10]:
	print(
		proc['proc'], '\n',
		proc['proc'].exe(), '\n',
		proc['mem'], '\n', 
		proc['info']['username'], '\n',
		proc['info']['memory_percent'], '\n\n\n'
		)
