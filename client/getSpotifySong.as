#!/bin/bash
osascript <<EOD
on write_to_file(this_data, target_file, append_data) -- (string, file path as string, boolean)
    try
        set the target_file to the target_file as text
        set the open_target_file to ¬
            open for access file target_file with write permission
        if append_data is false then ¬
            set eof of the open_target_file to 0
        write this_data to the open_target_file starting at eof
        close access the open_target_file
    on error
        try
            close access file target_file
        end try
    end try
end write_to_file

tell application "Spotify"
	set theTrack to current track
	set theArtist to artist of theTrack
	set theName to name of theTrack
	if player state is playing then
		set playStatus to "playing"
	else 
		set playStatus to "notPlaying"
	end if
end tell

set theValue to theName & "\n" & theArtist & "\n" & playStatus

write_to_file(theValue, (((path to home folder) as text) & "nowplaying.txt"), false)

EOD
