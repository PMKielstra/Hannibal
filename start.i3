for_window [class=".*"] fullscreen enable

exec --no-startup-id unclutter --timeout 1
exec --no-startup-id kaylee
exec python3 imgview.py