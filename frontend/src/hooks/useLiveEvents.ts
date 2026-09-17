import { useEffect, useRef, useState } from "react";
import { wsUrl } from "@/services/api";
import type { WsMessage } from "@/types";

/**
 * Connects to /ws/events and keeps a rolling buffer of the most recent
 * messages. Reconnects automatically with a short backoff if the connection
 * drops — useful during a live demo where the backend might restart.
 */
export function useLiveEvents(maxItems = 50) {
  const [messages, setMessages] = useState<WsMessage[]>([]);
  const [connected, setConnected] = useState(false);
  const retryRef = useRef<number>(0);

  useEffect(() => {
    let socket: WebSocket;
    let cancelled = false;
    let retryTimeout: ReturnType<typeof setTimeout>;

    function connect() {
      socket = new WebSocket(wsUrl("/ws/events"));

      socket.onopen = () => {
        if (cancelled) return;
        setConnected(true);
        retryRef.current = 0;
      };

      socket.onmessage = (event) => {
        try {
          const parsed: WsMessage = JSON.parse(event.data);
          setMessages((prev) => [parsed, ...prev].slice(0, maxItems));
        } catch {
          /* ignore malformed frame */
        }
      };

      socket.onclose = () => {
        if (cancelled) return;
        setConnected(false);
        const delay = Math.min(1000 * 2 ** retryRef.current, 10000);
        retryRef.current += 1;
        retryTimeout = setTimeout(connect, delay);
      };

      socket.onerror = () => socket.close();
    }

    connect();
    return () => {
      cancelled = true;
      clearTimeout(retryTimeout);
      socket?.close();
    };
  }, [maxItems]);

  return { messages, connected };
}
