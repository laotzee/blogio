#!/bin/bash

blogio="~/blogio/scripts"

# Function to safely add a cron job
# Parameters:
#   $1: CRON_SCHEDULE ("0 8 * * *")
#   $2: COMMAND_TO_RUN ("/path/to/script.sh")
#   $3: UNIQUE_COMMENT ('# descriptive comment')
add_safe_cron_job() {
    local schedule="$1"
    local command="$2"
    local unique_id="$3"
    local cron_entry

    if [ -z "$schedule" ] || [ -z "$command" ] || [ -z "$unique_id" ]; then
        echo "ERROR: Missing parameters. Usage: add_safe_cron_job <schedule> <command> <unique_id>"
        return 1
    fi

    cron_entry="${schedule} ${command} 2>&1 ${unique_id}"

    echo "--- Checking for Job: ${unique_id} ---"
    
    if crontab -l 2>/dev/null | grep -Fq "$unique_id"; then
        echo "--> Job already exists. Skipping installation."
    else
        echo "--> Job not found. Installing..."
        
        (crontab -l 2>/dev/null; echo "$cron_entry") | crontab -
        
        if [ $? -eq 0 ]; then
            echo "SUCCESS: Job installed: ${cron_entry}"
        else
            echo "ERROR: Failed to install the cron job."
            return 1
        fi
    fi
    return 0
}


add_safe_cron_job \
    "0 9 * * *" \
    "$blogio/publish.sh" \
    "# Automatically publish posts at 9AM everyday"

add_safe_cron_job \
    "0 0 * * *" \
    "$blogio/run.sh" \
    "# Sync posts and process them"

# -----------------------------------------------------------------
echo ""
echo "Script complete"
echo "-----------------------------------------------------------------"
echo "To verify the installed jobs, run: crontab -l"
echo "To clean up all log files, run: rm -f /tmp/system_uptime.log"
echo "-----------------------------------------------------------------"
