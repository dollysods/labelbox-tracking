---
layout: default
title: Daily Tracking Reports
---

# Daily Tracking Reports

Download the latest tracking data below:

- [CSV Report](/labelbox-tracking/assets/tracking_data/{{LATEST_CSV}})
- [TXT Report](/labelbox-tracking/assets/tracking_data/{{LATEST_TXT}})

<button id="refresh-data">Refresh Data</button>
<p id="status-message"></p>

{% raw %}
<script>
  document.getElementById("refresh-data").addEventListener("click", async () => {
    const statusMessage = document.getElementById("status-message");
    statusMessage.textContent = "Refreshing data...";

    try {
      const response = await fetch("https://api.github.com/repos/dollysods/labelbox-tracking/dispatches", {
        method: "POST",
        headers: {
          "Accept": "application/vnd.github.v3+json",
        },
        body: JSON.stringify({
          event_type: "trigger-refresh" // Matches the event type in the workflow
        }),
      });

      if (response.ok) {
        statusMessage.textContent = "Workflow triggered successfully!";
      } else {
        statusMessage.textContent = `Failed to trigger workflow: ${response.statusText}`;
      }
    } catch (error) {
      statusMessage.textContent = `Error: ${error.message}`;
    }
  });
</script>
{% endraw %}
