const tg = window.Telegram && window.Telegram.WebApp;
if (tg) {
  tg.ready();
  tg.expand();
}

const gallery = document.getElementById("gallery");
const statusBox = document.getElementById("status");

async function loadMedia() {
  try {
    const res = await fetch("/api/media");
    const items = await res.json();

    statusBox.textContent = items.length
      ? `${items.length}টি media`
      : "এখনও কোনো media পাওয়া যায়নি।";

    gallery.innerHTML = "";

    for (const item of items) {
      const card = document.createElement("article");
      card.className = "card";

      const thumb = document.createElement("div");
      thumb.className = "thumb";

      if (item.type === "photo") {
        const img = document.createElement("img");
        img.src = `/media/${item.id}`;
        img.alt = "Photo";
        img.loading = "lazy";
        thumb.appendChild(img);
      } else {
        const video = document.createElement("video");
        video.src = `/media/${item.id}`;
        video.controls = true;
        video.preload = "metadata";
        thumb.appendChild(video);
      }

      const info = document.createElement("div");
      info.className = "info";

      const caption = document.createElement("div");
      caption.className = "caption";
      caption.textContent = item.caption || (item.type === "video" ? "Video" : "Photo");

      const button = document.createElement("button");
      button.className = "open";
      button.textContent = "📩 Telegram-এ পাঠান";
      button.onclick = () => sendToBot(item.id);

      info.appendChild(caption);
      info.appendChild(button);
      card.appendChild(thumb);
      card.appendChild(info);
      gallery.appendChild(card);
    }
  } catch (e) {
    statusBox.textContent = "❌ Media load করা যায়নি।";
  }
}

function sendToBot(id) {
  if (!tg) {
    alert("এই Website-টি Telegram Mini App হিসেবে খুলুন।");
    return;
  }

  tg.sendData(JSON.stringify({ media_id: id }));
  tg.close();
}

loadMedia();
