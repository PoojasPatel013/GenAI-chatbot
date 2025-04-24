document.addEventListener("DOMContentLoaded", () => {
    // Check API status
    checkApiStatus()
  
    // Mode switching
    const modeBtns = document.querySelectorAll(".mode-btn")
    const modeContainers = document.querySelectorAll(".mode-container")
  
    modeBtns.forEach((btn) => {
      btn.addEventListener("click", function () {
        // Remove active class from all buttons and containers
        modeBtns.forEach((b) => b.classList.remove("active"))
        modeContainers.forEach((c) => c.classList.remove("active"))
  
        // Add active class to clicked button
        this.classList.add("active")
  
        // Show corresponding container
        const mode = this.id.replace("-mode", "")
        document.getElementById(`${mode}-mode-container`).classList.add("active")
      })
    })
  
    // File upload handlers
    setupFileUpload("past-file-upload", "past-context")
    setupFileUpload("future-file-upload", "future-context")
    setupFileUpload("debate-past-upload", "debate-past-context")
    setupFileUpload("debate-future-upload", "debate-future-context")
  
    // Past Self Chat
    const pastSendBtn = document.getElementById("past-send-btn")
    const pastMessageInput = document.getElementById("past-message-input")
    const pastChatMessages = document.getElementById("past-chat-messages")
  
    pastSendBtn.addEventListener("click", () => {
      sendPastMessage()
    })
  
    pastMessageInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        sendPastMessage()
      }
    })
  
    function sendPastMessage() {
      const message = pastMessageInput.value.trim()
      if (!message) return
  
      // Add user message to chat
      addMessageToChat(pastChatMessages, message, "user-message")
  
      // Get past context
      const pastContext = document.getElementById("past-context").value.trim()
  
      // Clear input
      pastMessageInput.value = ""
  
      // Show loading indicator
      const loadingId = addLoadingMessage(pastChatMessages, "past-message")
  
      // Send to backend
      fetch("/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          mode: "past",
          message: message,
          context: pastContext,
        }),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`)
          }
          return response.json()
        })
        .then((data) => {
          // Remove loading message
          document.getElementById(loadingId).remove()
  
          if (data.error) {
            // Show error message
            addMessageToChat(pastChatMessages, `Error: ${data.error}`, "past-message error-message")
          } else {
            // Add response to chat
            addMessageToChat(pastChatMessages, data.response, "past-message")
          }
  
          // Scroll to bottom
          pastChatMessages.scrollTop = pastChatMessages.scrollHeight
        })
        .catch((error) => {
          // Remove loading message
          document.getElementById(loadingId).remove()
  
          // Add error message
          addMessageToChat(pastChatMessages, `Error: ${error.message}`, "past-message error-message")
          console.error("Error:", error)
        })
    }
  
    // Future Self Chat
    const futureSendBtn = document.getElementById("future-send-btn")
    const futureMessageInput = document.getElementById("future-message-input")
    const futureChatMessages = document.getElementById("future-chat-messages")
  
    futureSendBtn.addEventListener("click", () => {
      sendFutureMessage()
    })
  
    futureMessageInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        sendFutureMessage()
      }
    })
  
    function sendFutureMessage() {
      const message = futureMessageInput.value.trim()
      if (!message) return
  
      // Add user message to chat
      addMessageToChat(futureChatMessages, message, "user-message")
  
      // Get future context
      const futureContext = document.getElementById("future-context").value.trim()
  
      // Clear input
      futureMessageInput.value = ""
  
      // Show loading indicator
      const loadingId = addLoadingMessage(futureChatMessages, "future-message")
  
      // Send to backend
      fetch("/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          mode: "future",
          message: message,
          context: futureContext,
        }),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`)
          }
          return response.json()
        })
        .then((data) => {
          // Remove loading message
          document.getElementById(loadingId).remove()
  
          if (data.error) {
            // Show error message
            addMessageToChat(futureChatMessages, `Error: ${data.error}`, "future-message error-message")
          } else {
            // Add response to chat
            addMessageToChat(futureChatMessages, data.response, "future-message")
          }
  
          // Scroll to bottom
          futureChatMessages.scrollTop = futureChatMessages.scrollHeight
        })
        .catch((error) => {
          // Remove loading message
          document.getElementById(loadingId).remove()
  
          // Add error message
          addMessageToChat(futureChatMessages, `Error: ${error.message}`, "future-message error-message")
          console.error("Error:", error)
        })
    }
  
    // Debate Generation
    const generateDebateBtn = document.getElementById("generate-debate-btn")
    const debateResult = document.getElementById("debate-result")
  
    generateDebateBtn.addEventListener("click", () => {
      const pastContext = document.getElementById("debate-past-context").value.trim()
      const futureContext = document.getElementById("debate-future-context").value.trim()
      const topic = document.getElementById("debate-topic").value.trim()
  
      if (!pastContext || !futureContext || !topic) {
        alert("Please fill in all fields for the debate")
        return
      }
  
      // Show loading
      debateResult.innerHTML =
        '<div class="loading"><div></div><div></div><div></div><div></div></div> Generating debate...'
  
      // Send to backend
      fetch("/debate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          pastContext: pastContext,
          futureContext: futureContext,
          topic: topic,
        }),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`)
          }
          return response.json()
        })
        .then((data) => {
          if (data.error) {
            // Show error message
            debateResult.textContent = `Error: ${data.error}`
            debateResult.classList.add("error-message")
          } else {
            // Display debate
            debateResult.textContent = data.response
            debateResult.classList.remove("error-message")
          }
        })
        .catch((error) => {
          debateResult.textContent = `Error: ${error.message}`
          debateResult.classList.add("error-message")
          console.error("Error:", error)
        })
    })
  
    // Helper function to add messages to chat
    function addMessageToChat(chatElement, message, className) {
      const messageElement = document.createElement("div")
      messageElement.classList.add("message", className)
      messageElement.textContent = message
  
      // Generate a unique ID for the message
      const messageId = "msg-" + Date.now()
      messageElement.id = messageId
  
      chatElement.appendChild(messageElement)
  
      // Scroll to bottom
      chatElement.scrollTop = chatElement.scrollHeight
  
      return messageId
    }
  
    // Helper function to add loading animation
    function addLoadingMessage(chatElement, className) {
      const messageElement = document.createElement("div")
      messageElement.classList.add("message", className)
  
      const loadingDiv = document.createElement("div")
      loadingDiv.className = "loading"
      loadingDiv.innerHTML = "<div></div><div></div><div></div><div></div>"
  
      messageElement.appendChild(loadingDiv)
  
      // Generate a unique ID for the message
      const messageId = "loading-" + Date.now()
      messageElement.id = messageId
  
      chatElement.appendChild(messageElement)
  
      // Scroll to bottom
      chatElement.scrollTop = chatElement.scrollHeight
  
      return messageId
    }
  
    // Function to check API status
    function checkApiStatus() {
      const apiStatusContainer = document.getElementById("api-status-container")
  
      fetch("/check-api")
        .then((response) => response.json())
        .then((data) => {
          if (data.valid) {
            apiStatusContainer.innerHTML = `
              <div class="api-status success">
                <i class="fas fa-check-circle"></i> Gemini API connected successfully
              </div>
            `
          } else {
            apiStatusContainer.innerHTML = `
              <div class="api-status error">
                <i class="fas fa-exclamation-circle"></i> Gemini API key is invalid or not set
              </div>
            `
          }
        })
        .catch((error) => {
          apiStatusContainer.innerHTML = `
            <div class="api-status error">
              <i class="fas fa-exclamation-circle"></i> Error checking API status
            </div>
          `
          console.error("Error checking API status:", error)
        })
    }
  
    // Function to handle file uploads
    function setupFileUpload(inputId, targetTextareaId) {
      const fileInput = document.getElementById(inputId)
      const textarea = document.getElementById(targetTextareaId)
  
      fileInput.addEventListener("change", function () {
        if (this.files && this.files[0]) {
          const file = this.files[0]
  
          // Create FormData
          const formData = new FormData()
          formData.append("file", file)
  
          // Show loading notification
          const uploadNotification = document.createElement("div")
          uploadNotification.className = "file-notification"
          uploadNotification.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading file...'
  
          // Find the parent container for the textarea
          const textareaContainer = textarea.closest(".textarea-with-upload")
  
          // Remove any existing notification
          const existingNotification = textareaContainer.querySelector(".file-notification")
          if (existingNotification) {
            existingNotification.remove()
          }
  
          // Add notification after textarea
          textareaContainer.appendChild(uploadNotification)
  
          // Upload file
          fetch("/upload-journal", {
            method: "POST",
            body: formData,
          })
            .then((response) => response.json())
            .then((data) => {
              if (data.error) {
                uploadNotification.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${data.error}`
                uploadNotification.style.backgroundColor = "rgba(239, 68, 68, 0.1)"
                uploadNotification.style.color = "var(--error-color)"
              } else {
                // Update textarea with file content
                textarea.value = data.content
  
                // Update notification
                uploadNotification.innerHTML = `<i class="fas fa-check-circle"></i> File "${file.name}" uploaded successfully`
  
                // Remove notification after 3 seconds
                setTimeout(() => {
                  uploadNotification.remove()
                }, 3000)
              }
            })
            .catch((error) => {
              uploadNotification.innerHTML = `<i class="fas fa-exclamation-circle"></i> Error uploading file`
              uploadNotification.style.backgroundColor = "rgba(239, 68, 68, 0.1)"
              uploadNotification.style.color = "var(--error-color)"
              console.error("Error:", error)
            })
        }
      })
    }
  })
  