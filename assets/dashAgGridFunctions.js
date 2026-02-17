// assets/dashAgGridFunctions.js
window.dashAgGridFunctions = window.dashAgGridFunctions || {};

window.dashAgGridFunctions.DatePicker = class {
  init(params) {
    this.eInput = document.createElement("input");
    this.eInput.className = "ag-input";
    this.eInput.value = params.value || "";

    // Attach flatpickr
    this.fp = flatpickr(this.eInput, {
      dateFormat: "Y-m-d", // yyyy-mm-dd
      allowInput: true,
      defaultDate: params.value || null,
    });

    // Apply input mask (yyyy-mm-dd)
    if (typeof Inputmask !== "undefined") {
      Inputmask("9999-99-99").mask(this.eInput);
    }
  }

  getGui() {
    return this.eInput;
  }

  afterGuiAttached() {
    this.eInput.focus();
    if (this.fp) {
      this.fp.open();
    }
  }

  getValue() {
    return this.eInput.value;
  }

  destroy() {
    if (this.fp) {
      this.fp.destroy();
    }
  }

  isPopup() {
    return true;
  }
};

// assets/dashAgGridFunctions.js
window.dashAgGridFunctions.DateTimePicker = class {
  init(params) {
    this.eInput = document.createElement("input");
    this.eInput.className = "ag-input";
    this.eInput.value = params.value || "";

    // Apply input mask for datetime (yyyy-mm-dd HH:MM)
    if (typeof Inputmask !== "undefined") {
      Inputmask("9999-99-99 99:99").mask(this.eInput);
    }

    // Attach flatpickr with time
    this.fp = flatpickr(this.eInput, {
      enableTime: true,
      dateFormat: "Y-m-d H:i", // yyyy-mm-dd HH:MM
      allowInput: true,
      defaultDate: params.value || null,
      time_24hr: true
    });
  }

  getGui() {
    return this.eInput;
  }

  afterGuiAttached() {
    this.eInput.focus();
    if (this.fp) {
      this.fp.open();
    }
  }

  getValue() {
    return this.eInput.value;
  }

  destroy() {
    if (this.fp) {
      this.fp.destroy();
    }
  }

  isPopup() {
    return true;
  }
};

// Searchable dropdown editor
window.dashAgGridFunctions.SearchableDropdownEditor = class {
	init(params) {
		this.params = params;
		this.eInput = document.createElement("input");
		this.eInput.className = "ag-input";
		this.eInput.value = params.value || "";

		// Ensure options exist
		this.options = params.colDef.cellEditorParams?.values || [];

		// Create the dropdown safely
		this.dropdown = document.createElement("div");
		if (this.dropdown) {
			this.dropdown.style.position = "absolute";
			this.dropdown.style.border = "1px solid #555";
			this.dropdown.style.background = "#2b2b2b";
			this.dropdown.style.color = "#eee";
			this.dropdown.style.fontFamily = "Arial, sans-serif";
			this.dropdown.style.fontSize = "13px";
			this.dropdown.style.maxHeight = "150px";
			this.dropdown.style.overflowY = "auto";
			this.dropdown.style.display = "none";
			this.dropdown.style.zIndex = 1000;
			this.dropdown.style.borderRadius = "4px";
			this.dropdown.style.boxShadow = "0 2px 6px rgba(0,0,0,0.5)";

			document.body.appendChild(this.dropdown);
		} else {
			console.warn("Dropdown element could not be created");
		}

		// Event listeners
		this.eInput.addEventListener("focus", () => this.showDropdown());

		this.onClickOutside = (event) => {
			if (!this.eInput.contains(event.target) && !this.dropdown.contains(event.target)) {
				this.hideDropdown();
				this.params.api.stopEditing();
			}
		};
		document.addEventListener("mousedown", this.onClickOutside);

		this.eInput.addEventListener("input", () => this.updateDropdown());
		this.eInput.addEventListener("keydown", (e) => this.onKeyDown(e));
	}


  getGui() {
    return this.eInput;
  }

  afterGuiAttached() {
    this.eInput.focus();
    this.updateDropdown();
  }

  getValue() {
    const value = this.eInput.value;
    const isValid = this.options.includes(value);
    return isValid ? value : null;  // or return "" or throw error
  }


  destroy() {
    this.hideDropdown();
    document.removeEventListener("mousedown", this.onClickOutside);
    if (this.dropdown.parentNode) this.dropdown.parentNode.removeChild(this.dropdown);
  }

  isPopup() {
    return true;
  }

  showDropdown() {
    this.dropdown.style.display = "block";
    this.updateDropdown();
    const rect = this.eInput.getBoundingClientRect();
    this.dropdown.style.left = rect.left + "px";
    this.dropdown.style.top = rect.bottom + "px";
    this.dropdown.style.width = rect.width + "px";
  }

  hideDropdown() {
    this.dropdown.style.display = "none";
  }

  updateDropdown() {
    const filter = this.eInput.value.toLowerCase();
    this.dropdown.innerHTML = "";
    const filtered = this.options.filter(o => o.toLowerCase().includes(filter));

    filtered.forEach(option => {
      const div = document.createElement("div");
      div.textContent = option;
      div.style.padding = "4px";
      div.style.cursor = "pointer";
      div.addEventListener("mousedown", (e) => {
        e.preventDefault();
        this.eInput.value = option;
        this.params.api.stopEditing();
        this.hideDropdown();
      });
      this.dropdown.appendChild(div);
    });

    if (filtered.length === 0) {
      const empty = document.createElement("div");
      empty.textContent = "No matches";
      empty.style.padding = "4px";
      empty.style.color = "#999";
      this.dropdown.appendChild(empty);
    }
  }

  onKeyDown(e) {
    const items = Array.from(this.dropdown.children);
    if (!items.length) return;

    let selectedIndex = items.findIndex(i => i.classList.contains("selected"));

    if (e.key === "ArrowDown") {
      if (selectedIndex >= 0) items[selectedIndex].classList.remove("selected");
      selectedIndex = (selectedIndex + 1) % items.length;
      items[selectedIndex].classList.add("selected");
      e.preventDefault();
    } else if (e.key === "ArrowUp") {
      if (selectedIndex >= 0) items[selectedIndex].classList.remove("selected");
      selectedIndex = (selectedIndex - 1 + items.length) % items.length;
      items[selectedIndex].classList.add("selected");
      e.preventDefault();
    } else if (e.key === "Enter") {
      if (selectedIndex >= 0) {
        this.eInput.value = items[selectedIndex].textContent;
        this.params.api.stopEditing();
        this.hideDropdown();
        e.preventDefault();
      }
    }
  }
};