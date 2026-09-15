import React, { useState, useRef, useEffect } from "react";
import { Send, Sparkles, Volume2, Mic, MicOff, Check, CornerDownLeft } from "lucide-react";
import { ChatMessage } from "../types";

interface ChatViewProps {
  messages: ChatMessage[];
  onSendMessage: (text: string) => Promise<void>;
  isLoading: boolean;
}

export const ChatView: React.FC<ChatViewProps> = ({ messages, onSendMessage, isLoading }) => {
  const [inputText, setInputText] = useState("");
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || isLoading) return;
    const text = inputText;
    setInputText("");
    await onSendMessage(text);
  };

  const handleSpeak = (text: string) => {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  };

  const toggleMic = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in this browser environment. Type your message below.");
      return;
    }

    if (isListening) {
      setIsListening(false);
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = "en-US";

      recognition.onstart = () => setIsListening(true);
      recognition.onend = () => setIsListening(false);
      recognition.onerror = () => setIsListening(false);
      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputText(transcript);
        setIsListening(false);
      };

      recognition.start();
    } catch {
      setIsListening(false);
    }
  };

  const quickPrompts = [
    "What time is it?",
    "Plan my day",
    "Remember my favorite color is ocean blue",
    "What is my favorite color?",
    "I am feeling stressed with deadlines",
    "Add a task: Review security audit logs",
    "Show tasks"
  ];

  const getEmotionColor = (emotion?: string) => {
    switch (emotion) {
      case "HAPPY":
      case "EXCITED":
        return "bg-emerald-50 text-emerald-700 border-emerald-200";
      case "STRESSED":
      case "ANGRY":
        return "bg-amber-50 text-amber-700 border-amber-200";
      case "SAD":
      case "TIRED":
        return "bg-blue-50 text-blue-700 border-blue-200";
      default:
        return "bg-neutral-100 text-neutral-700 border-neutral-200";
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8.5rem)] max-w-5xl mx-auto">
      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-5">
        {messages.length === 0 ? (
          <div className="text-center py-16 px-4">
            <div className="w-12 h-12 rounded-2xl bg-neutral-100 border border-neutral-200 flex items-center justify-center mx-auto mb-4 text-neutral-800">
              <Sparkles className="w-6 h-6" />
            </div>
            <h2 className="text-lg font-semibold text-neutral-900 mb-1">
              Welcome to MY AI
            </h2>
            <p className="text-sm text-neutral-500 max-w-md mx-auto mb-6">
              Your personal assistant and companion running 100% locally with private deterministic logic and custom neural models.
            </p>
            <div className="flex flex-wrap gap-2 justify-center max-w-lg mx-auto">
              {quickPrompts.slice(0, 4).map((prompt, idx) => (
                <button
                  key={idx}
                  id={`prompt-${idx}`}
                  onClick={() => onSendMessage(prompt)}
                  className="text-xs px-3 py-1.5 rounded-full border border-neutral-200 bg-white hover:bg-neutral-50 text-neutral-700 transition-colors shadow-2xs"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex flex-col ${msg.sender === "user" ? "items-end" : "items-start"}`}
            >
              <div
                className={`max-w-2xl px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                  msg.sender === "user"
                    ? "bg-neutral-900 text-white rounded-br-xs"
                    : "bg-white border border-neutral-200 text-neutral-800 shadow-2xs rounded-bl-xs"
                }`}
              >
                <div className="whitespace-pre-wrap">{msg.text}</div>

                {/* Metadata tags for assistant responses */}
                {msg.sender === "assistant" && (
                  <div className="mt-2.5 pt-2 border-t border-neutral-100 flex flex-wrap items-center gap-2 text-2xs text-neutral-500">
                    {msg.intent && (
                      <span className="font-mono bg-neutral-100 px-1.5 py-0.5 rounded border border-neutral-200">
                        {msg.intent} {msg.confidence ? `(${Math.round(msg.confidence * 100)}%)` : ""}
                      </span>
                    )}
                    {msg.emotion && (
                      <span className={`px-1.5 py-0.5 rounded border font-medium ${getEmotionColor(msg.emotion)}`}>
                        {msg.emotion}
                      </span>
                    )}
                    <button
                      onClick={() => handleSpeak(msg.text)}
                      title="Speak response"
                      className="hover:text-neutral-900 ml-auto flex items-center gap-1 text-neutral-400 hover:text-neutral-700 transition-colors"
                    >
                      <Volume2 className="w-3.5 h-3.5" />
                      <span>Speak</span>
                    </button>
                  </div>
                )}
              </div>
              <span className="text-2xs text-neutral-400 mt-1 px-1">{msg.timestamp}</span>
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex items-start">
            <div className="bg-white border border-neutral-200 px-4 py-3 rounded-2xl rounded-bl-xs text-xs text-neutral-500 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-neutral-400 animate-pulse"></span>
              <span>MY AI is thinking and processing locally...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested chips above input */}
      <div className="px-4 py-2 border-t border-neutral-100 flex items-center gap-2 overflow-x-auto no-scrollbar">
        <span className="text-2xs font-semibold text-neutral-400 uppercase tracking-wider whitespace-nowrap">Try:</span>
        {quickPrompts.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => onSendMessage(prompt)}
            className="text-xs px-2.5 py-1 rounded-full border border-neutral-200 bg-neutral-50 hover:bg-neutral-100 text-neutral-600 transition-colors whitespace-nowrap"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Box */}
      <div className="p-4 bg-white border-t border-neutral-200">
        <form onSubmit={handleSubmit} className="relative flex items-center">
          <input
            id="chat-input"
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Type a message, question, reminder, or task..."
            disabled={isLoading}
            className="w-full pl-4 pr-24 py-3 text-sm bg-neutral-50 border border-neutral-300 rounded-xl focus:outline-none focus:border-neutral-900 focus:ring-1 focus:ring-neutral-900 transition-all text-neutral-900 placeholder:text-neutral-400"
          />
          <div className="absolute right-2 flex items-center gap-1.5">
            <button
              type="button"
              id="mic-button"
              onClick={toggleMic}
              title={isListening ? "Listening..." : "Click to speak"}
              className={`p-1.5 rounded-lg border text-neutral-600 transition-colors ${
                isListening
                  ? "bg-rose-50 text-rose-600 border-rose-300 animate-pulse"
                  : "hover:bg-neutral-200 border-transparent text-neutral-500"
              }`}
            >
              {isListening ? <Mic className="w-4 h-4" /> : <MicOff className="w-4 h-4" />}
            </button>
            <button
              type="submit"
              id="send-button"
              disabled={!inputText.trim() || isLoading}
              className="p-1.5 rounded-lg bg-neutral-900 text-white hover:bg-neutral-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <CornerDownLeft className="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
