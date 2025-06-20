#!/bin/bash

DESTINATION="/home/astappiev/nocode-er-bench/apptainer"
METHODS=(
    "/home/astappiev/nocode-er-bench/methods/deepmatcher"
    "/home/astappiev/nocode-er-bench/methods/ditto"
    "/home/astappiev/nocode-er-bench/methods/emtransformer"
    "/home/astappiev/nocode-er-bench/methods/gnem"
    "/home/astappiev/nocode-er-bench/methods/hiermatcher"
    "/home/astappiev/nocode-er-bench/methods/magellan"
    "/home/astappiev/nocode-er-bench/methods/zeroer"

    "/home/astappiev/nocode-er-bench/splitters/Random"
    "/home/astappiev/nocode-er-bench/splitters/KNN-Join"
    "/home/astappiev/nocode-er-bench/splitters/DeepBlocker"
)

COMMAND="apptainer build --force"
MAX_PARALLEL=5
FAILED_LIST=$(mktemp)  # Create a temporary file to track failed tasks

log() {
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S");
    echo "[$timestamp]" "$@";
}

process_container() {
    local folder=$1
    local name=$(basename "$folder")
    # Rename special cases
    if [ "$name" == "Random" ]; then
        name="splitter_random"
    elif [ "$name" == "KNN-Join" ]; then
        name="splitter_knnjoin"
    elif [ "$name" == "DeepBlocker" ]; then
        name="splitter_deepblocker"
    fi

    log "Starting: $name"

    if [ ! -d "$folder" ]; then
        log "❌ Error: Folder does not exist: $folder"
        echo "$name" >> "$FAILED_LIST"  # Record failure
        return 1
    fi

    (cd "$folder" && eval "$COMMAND $DESTINATION/${name}.sif container.def")
    local result=$?
    
    timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    if [ $result -eq 0 ]; then
        log "✅ Success: $name"
        return 0
    else
        log "❌ Failed: $name (exit code: $result)"
        echo "$name" >> "$FAILED_LIST"  # Record failure
        return 1
    fi
}

# Process folders in parallel
log "Processing ${#METHODS[@]} folders with maximum $MAX_PARALLEL parallel jobs"

# Use a simple approach with background processes
pids=()
failures=0

for folder in "${METHODS[@]}"; do
    # If we're at max parallel, wait for one to finish
    while [ ${#pids[@]} -ge $MAX_PARALLEL ]; do
        for i in "${!pids[@]}"; do
            if ! kill -0 "${pids[i]}" 2>/dev/null; then
                wait "${pids[i]}" || ((failures++))
                unset pids[i]
                pids=("${pids[@]}")  # Reindex array
                break
            fi
        done
        sleep 0.1  # Small sleep to avoid CPU spinning
    done
    
    # Start a new process
    process_container "$folder" &
    pids+=($!)
done

# Wait for any remaining processes
for pid in "${pids[@]}"; do
    wait "$pid" || ((failures++))
done

# Print summary
echo ""
echo "=== Summary ==="
echo "Total folders: ${#METHODS[@]}"
if [ $failures -eq 0 ]; then
    log "✅ All folders processed successfully."
    rm -f "$FAILED_LIST"  # Clean up temporary file
    exit 0
else
    log "❌ $failures folder(s) failed. Check the output above for details."
    echo "Failed tasks:"
    cat "$FAILED_LIST" | sort | uniq | sed 's/^/  - /'  # Print formatted list of failed tasks
    rm -f "$FAILED_LIST"  # Clean up temporary file
    exit 1
fi
