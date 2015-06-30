$scripts = @('ttswhi.py','ttswhi_gui.py','ttsanr.py','ttsanr_gui.py')
foreach ($script in $scripts)
{
	write-host 'Compiling '$script
	$command = 'pyinstaller -y -c -F --log-level WARN '+$script
	iex $command
}