---
layout: default
title: Daily Tracking Reports
---

# Daily Tracking Reports

Download the latest tracking data below:

<!-- TRACKING_DATA_LINKS -->

<a href="#" id="refresh-link">Refresh Data</a>
<p id="status-message"></p>

<script>
  document.getElementById("refresh-link").addEventListener("click", async (event) => {
  event.preventDefault(); // Prevent the link from navigating away

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
      const errorDetails = await response.json();
      statusMessage.textContent = `Failed to trigger workflow: ${response.status} ${response.statusText}. Error: ${errorDetails.message}`;
    }
  } catch (error) {
    statusMessage.textContent = `Error: ${error.message}`;
  }
});
</script>
