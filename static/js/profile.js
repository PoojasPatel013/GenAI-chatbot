import { Chart } from "@/components/ui/chart"
document.addEventListener("DOMContentLoaded", () => {
  // Fetch user stats
  fetchUserStats()

  // Change password button
  const changePasswordBtn = document.getElementById("change-password-btn")
  if (changePasswordBtn) {
    changePasswordBtn.addEventListener("click", () => {
      alert("This feature is coming soon!")
    })
  }

  // Export data button
  const exportDataBtn = document.getElementById("export-data-btn")
  if (exportDataBtn) {
    exportDataBtn.addEventListener("click", () => {
      alert("This feature is coming soon!")
    })
  }

  // Function to fetch user stats
  function fetchUserStats() {
    // This would normally be an API call, but for now we'll just simulate it
    const totalChatsElement = document.getElementById("total-chats")

    // Count the number of chat items in the sidebar (this is a simple approach)
    const chatItems = document.querySelectorAll(".chat-item")
    if (totalChatsElement) {
      totalChatsElement.textContent = chatItems.length || "0"
    }

    // Initialize usage chart
    initializeUsageChart()
  }

  // Function to initialize usage chart
  function initializeUsageChart() {
    const ctx = document.getElementById("usage-chart")

    if (ctx) {
      // This would normally be data from an API, but for now we'll use dummy data
      new Chart(ctx, {
        type: "doughnut",
        data: {
          labels: ["Past Self", "Future Self", "Time-Travel Debate"],
          datasets: [
            {
              data: [40, 35, 25],
              backgroundColor: [
                "#06b6d4", // past-color
                "#fbbf24", // future-color
                "#8b5cf6", // debate-color
              ],
              borderWidth: 0,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false,
            },
            tooltip: {
              callbacks: {
                label: (context) => `${context.label}: ${context.raw}%`,
              },
            },
          },
          cutout: "70%",
        },
      })
    }
  }
})
