require('dotenv').config();
const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();
app.use(cors());
app.use(express.json());

// Contact form endpoint
app.post('/contact', async (req, res) => {
  try {
    const { first_name, last_name, user_email, subject, message } = req.body;

    if (!first_name || !last_name || !user_email || !subject || !message) {
      return res.status(400).json({ success: false, error: 'All fields are required!' });
    }

    const telegramMessage = `
📩 *New Contact Form Submission*
━━━━━━━━━━━━━━━
👤 *Name:* ${first_name} ${last_name}
📧 *Email:* ${user_email}
📝 *Subject:* ${subject}

💬 *Message:*
${message}
━━━━━━━━━━━━━━━
    `;

    await axios.post(`https://api.telegram.org/bot${process.env.TELEGRAM_TOKEN}/sendMessage`, {
      chat_id: process.env.CHAT_ID,
      text: telegramMessage,
      parse_mode: 'Markdown'
    });

    res.json({ success: true, message: 'Message sent to Telegram successfully!' });
  } catch (error) {
    console.error('Error sending message:', error.response?.data || error.message);
    res.status(500).json({ success: false, error: 'Failed to send message to Telegram.' });
  }
});

app.listen(process.env.PORT || 3000, () => {
  console.log('Backend running...');
});
