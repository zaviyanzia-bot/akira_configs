Created At: 2026-06-30T21:13:56Z
Completed At: 2026-06-30T21:13:58Z

				The command completed successfully.
				Output:
				620 (indent 20): '                    self.last_error_reason = "REGION_RESTRICTED"'
621 (indent 20): '                    self.log("ERROR", f"Row {row_id}: All {max_nav_attempts} navigation attempts failed due to region restriction.")'
622 (indent 20): '                    raise Exception("PAGE_NOT_LOADED")'
623 (indent 0): ''
624 (indent 16): '                self._minimize_chrome()'
625 (indent 0): ''
626 (indent 16): '                # First time / Login setup mode'
627 (indent 16): '                if setup_mode:'
628 (indent 20): '                    self.log("SYSTEM", f"Row {row_id}: Launcher running in headful setup mode. Please log in to AI Chat in the browser window.")'
629 (indent 20): '                    self.update_status(row_id, "SUBMITTING", "Waiting for manual Google login...")'
630 (indent 20): '                    # Poll for 2 minutes or until "Log In" button disappears (indicating login success)'
631 (indent 20): '                    for i in range(120):'
632 (indent 24): '                        if getattr(self, "is_stopped", False):'
633 (indent 28): '                            break'
634 (indent 24): '                        try:'
635 (indent 28): '                            if page.locator(\'a:has-text("Log In")\').is_visible(timeout=500):'
636 (indent 32): '                                page.wait_for_timeout(1000)'
637 (indent 32): '                                continue'
638 (indent 28): '                            else:'
639 (indent 32): '                                self.log("SUCCESS", f"Row {row_id}: Google login detected! Session established.")'
640 (indent 32): '                                break'
641 (indent 24): '                        except Exception:'
642 (indent 28): '                            break'
643 (indent 20): '                    context.storage_state(path=os.path.join(self.profile_dir_master, "auth_state.json"))'
644 (indent 20): '                    self.log("SUCCESS", f"Row {row_id}: Master profile auth state saved.")'
645 (indent 20): '                    return True'
646 (indent 0): ''
647 (indent 24): '                        # 1. Wait for page to load or click "Log In" if needed'
648 (indent 24): '                        try:'
649 (indent 28): '                            # Wait up to 15 seconds for either the phone input or the Log In button to appear'
650 (indent 28): '                            for wait_sec in range(15):'
651 (indent 32): '                                if getattr(self, "is_stopped", False):'
652 (indent 36): '                                    break'
653 (indent 32): '                                # If phone input is already there, we can proceed'
654 (indent 32): '                                phone_input = page.locator(\'input[type="tel"], input[placeholder*="Phone"], input[placeholder*="number"]\').first'
655 (indent 32): '                                if phone_input.count() > 0 and phone_input.is_visible():'
656 (indent 36): '                                    break'
657 (indent 0): ''
658 (indent 32): '                                # Otherwise, look for Log In button and click it'
659 (indent 32): '                                login_btn = page.locator(\'button:has-text("Log In"), a:has-text("Log In"), [role="button"]:has-text("Log In")\').first'
660 (indent 32): '                                if login_btn.count() > 0 and login_btn.is_visible():'

