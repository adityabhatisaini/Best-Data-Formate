const state = {
  summary: window.__BOOTSTRAP__.summary,
  devices: window.__BOOTSTRAP__.devices,
  activity: window.__BOOTSTRAP__.activity,
};

const summaryGrid = document.getElementById("summaryGrid");
const deviceTable = document.getElementById("deviceTable");
const activityFeed = document.getElementById("activityFeed");
const toast = document.getElementById("toast");
const actionState = document.getElementById("actionState");
const policySelect = document.getElementById("policySelect");
const deviceSelect = document.getElementById("deviceSelect");

document.querySelectorAll("[data-action]").forEach((button) => {
  button.addEventListener("click", async () => {
    const actionName = button.dataset.action;
    actionState.textContent = "Running";
    button.disabled = true;

    try {
      const response = await fetch(`/api/actions/${actionName}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          policy_id: policySelect.value,
          device_id: deviceSelect.value,
        }),
      });
      const result = await response.json();
      if (!response.ok || !result.ok) {
        throw new Error(result.message || "Action failed.");
      }
      showToast(result.message, false);
      if (result.summary) {
        state.summary = result.summary;
        renderSummary();
      }
      if (result.devices) {
        state.devices = result.devices;
        renderDevices();
      }
      if (result.activity) {
        state.activity = result.activity;
        renderActivity();
      }
    } catch (error) {
      showToast(error.message, true);
    } finally {
      actionState.textContent = "Idle";
      button.disabled = false;
    }
  });
});

function renderSummary() {
  summaryGrid.querySelectorAll("[data-summary]").forEach((item) => {
    item.textContent = state.summary[item.dataset.summary] ?? "-";
  });
}

function renderDevices() {
  deviceTable.innerHTML = state.devices
    .map(
      (device) => `
        <tr>
          <td>${device.name}</td>
          <td><span class="status-pill ${device.status.toLowerCase().replaceAll(" ", "-")}">${device.status}</span></td>
          <td>${device.owner}</td>
          <td>${device.last_sync}</td>
        </tr>
      `,
    )
    .join("");
}

function renderActivity() {
  activityFeed.innerHTML = state.activity
    .map(
      (item) => `
        <article class="timeline-item">
          <span class="timeline-dot ${item.level}"></span>
          <div>
            <strong>${item.message}</strong>
            <p>${item.timestamp}</p>
          </div>
        </article>
      `,
    )
    .join("");
}

function showToast(message, isError) {
  toast.textContent = message;
  toast.classList.remove("hidden", "error");
  if (isError) {
    toast.classList.add("error");
  }
}
