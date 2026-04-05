(function initAuthUI(global) {
  function preventEvent(event) {
    if (!event) {
      return;
    }

    if (typeof event.preventDefault === "function") {
      event.preventDefault();
    }

    if (typeof event.stopPropagation === "function") {
      event.stopPropagation();
    }

    // Legacy fallback for inline handlers inside submit-capable containers.
    event.returnValue = false;
    event.cancelBubble = true;
  }

  function createMessageLogger(messageElementId = "message") {
    const messageElement = document.getElementById(messageElementId);
    const history = [];

    function sync(isError) {
      if (!messageElement) {
        return;
      }

      messageElement.classList.add("auth-message-log");
      if (isError) {
        messageElement.classList.add("auth-message-error");
      } else {
        messageElement.classList.remove("auth-message-error");
      }
      messageElement.textContent = history.join("\n");
    }

    function reset() {
      history.length = 0;
      sync(false);
    }

    function append(message, isError = false) {
      if (!messageElement || !message) {
        return;
      }

      const normalizedMessage = String(message);
      if (history[history.length - 1] !== normalizedMessage) {
        history.push(normalizedMessage);
      }

      sync(isError);
    }

    return {
      reset,
      append,
      element: messageElement,
    };
  }

  global.AuthUI = {
    preventEvent,
    createMessageLogger,
  };
})(window);
