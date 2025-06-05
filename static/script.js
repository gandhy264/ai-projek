document.addEventListener("DOMContentLoaded", () => {
  const chatForm = document.getElementById("chat-form");
  const chatBox = document.getElementById("chat-box");
  const userInput = document.getElementById("user-input");

  // Fungsi untuk menambahkan pesan ke chat box
  const addMessage = (message, sender) => {
    const bubble = document.createElement("div");
    bubble.classList.add("chat-bubble", sender);

    // Nama pengirim
    const senderName = document.createElement("div");
    senderName.classList.add("sender-name");
    senderName.innerHTML = sender === "user" ? "<b>Pelanggan :</b>" : "Admin :";
    bubble.appendChild(senderName);

    // Isi pesan
    const messageText = document.createElement("div");
    messageText.classList.add("message-text");
    messageText.textContent = message;
    bubble.appendChild(messageText);

    chatBox.appendChild(bubble);
    chatBox.scrollTop = chatBox.scrollHeight; // scroll ke bawah
  };

  // Event listener untuk form submit
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const message = userInput.value.trim();
    if (!message) return;

    // Tambahkan pesan user ke chat box
    addMessage(message, "user");
    userInput.value = "";

    try {
      // Kirim pesan ke server
      const response = await fetch("/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message }),
      });

      const data = await response.json();

      // Tampilkan balasan bot langsung tanpa efek mengetik
      addMessage(data.reply, "bot");
    } catch (error) {
      addMessage("Maaf, terjadi kesalahan. Silakan coba lagi.", "bot");
    }
  });
});
