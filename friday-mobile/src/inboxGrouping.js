const clean = (value) => String(value || "").trim();

const senderKey = (value) => clean(value).toLocaleLowerCase("de-DE") || "unbekannt";

const addItem = (target, item) => {
  if (!item || !item.sender) {
    return;
  }
  const key = senderKey(item.sender);
  const group = target.get(key) || {
    key,
    sender: item.sender,
    items: [],
    sources: new Set(),
    latestAt: "",
  };
  group.items.push(item);
  group.sources.add(item.sourceLabel);
  if (clean(item.receivedAt) > group.latestAt) {
    group.latestAt = clean(item.receivedAt);
  }
  target.set(key, group);
};

export function groupInboxItems({ messages = [], emailItems = [], mailItems = [], whatsappItems = [] }) {
  const groups = new Map();

  messages
    .filter((item) => !["whatsapp", "ms_mail", "imap_mail"].includes(clean(item?.source)))
    .forEach((item) => addItem(groups, {
      key: `message-${item.id}`,
      sender: clean(item.sender) || "Unbekannt",
      title: "Nachricht",
      body: clean(item.text),
      receivedAt: clean(item.received_at),
      source: clean(item.source) || "message",
      sourceLabel: "Friday",
      localMessageId: item.id,
      spamRef: item.id,
      raw: item,
    }));

  emailItems.forEach((item, index) => addItem(groups, {
    key: `email-${item.id || index}`,
    sender: clean(item.sender) || "Unbekannt",
    title: clean(item.subject) || "(ohne Betreff)",
    body: clean(item.text_preview || item.snippet),
    receivedAt: clean(item.date || item.received_at),
    source: "email",
    sourceLabel: "E-Mail",
    spamRef: item.id || index,
    raw: item,
  }));

  mailItems.forEach((item, index) => addItem(groups, {
    key: `mail-${item.message_id || item.id || index}`,
    sender: clean(item.sender) || "Unbekannt",
    title: clean(item.subject) || "(ohne Betreff)",
    body: clean(item.snippet || item.body_full),
    receivedAt: clean(item.received_at),
    source: clean(item.source) || "ms_mail",
    sourceLabel: item.source === "imap_mail" ? "Gmail" : "Microsoft",
    spamRef: item.message_id || item.id || index,
    raw: item,
  }));

  whatsappItems.forEach((item, index) => addItem(groups, {
    key: `whatsapp-${item.id || index}`,
    sender: clean(item.sender_name) || "WhatsApp",
    title: "WhatsApp",
    body: clean(item.body),
    receivedAt: clean(item.received_at),
    source: "whatsapp",
    sourceLabel: "WhatsApp",
    spamRef: item.id || index,
    raw: item,
  }));

  return [...groups.values()]
    .map((group) => ({
      ...group,
      count: group.items.length,
      sources: [...group.sources],
      items: group.items.sort((left, right) => clean(right.receivedAt).localeCompare(clean(left.receivedAt))),
    }))
    .sort((left, right) => right.latestAt.localeCompare(left.latestAt));
}
