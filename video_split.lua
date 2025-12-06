function split(s,d)
	s=s..d
	print(s)
	d=string.gsub(d,'([().%%+-*?%[%]%^$])','%%%1')
	local t={}
	for i in string.gmatch(s,'(.-)'..d) do
		t[#t+1]=i
	end
	return t
end

f=arg[1]
if not f then print(string.format([[This program splitting video or audio to files with duration.
	usage: lua %s /path/to/file duration]],arg[0])) os.exit() end 
fs=split(f,'.')
for k,v in pairs(fs) do print(k,v) end
dlit=tonumber(arg[2]) 

os.execute('ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "'..f..'" >dur')
io.input('dur')
duration=io.read()
os.remove('dur')
duration = tonumber(duration)
count = math.floor(duration / dlit)
if (duration % dlit) ~= 0 then count=count+1 end
print(duration,count)

cur=0
for i = 1,count do
	cmd='ffmpeg -i "%s" -ss %d -t %d -c copy "%s_%d.%s"'
	cmd=string.format(cmd,f,cur,dlit,fs[1],i,fs[2])
	print(cmd)
	cur=cur+dlit
	os.execute(cmd)
end
