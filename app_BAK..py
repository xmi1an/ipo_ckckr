import streamlit as st
import requests
import pandas as pd

# API URLs
API_URL = st.secrets["API_URL"]
API_URL2_BASE = st.secrets["API_URL2_BASE"]

PASSCODE = st.secrets["PASSCODE"]


# Retry mechanism for API calls
def fetch_data(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from {url}: {e}")
        return None


# Fetch IPO data from the first API
@st.cache_data(ttl=600)  # Cache IPO data for 10 minutes
def fetch_ipo_data():
    data = fetch_data(API_URL)
    if data and data.get("status"):
        return data["data"]
    return []


# Fetch allotment data from the second API
def fetch_allotment_data(registrar, company_id, pan_number):
    url = f"{API_URL2_BASE}/{registrar}?company_id={company_id}&pan={pan_number}"
    data = fetch_data(url)
    if data and data.get("status"):
        return data["data"]
    return None


# Validate PAN number format (basic validation)
def validate_pan(pan_number):
    if not pan_number or len(pan_number) != 10 or not pan_number.isalnum():
        return False
    return True


# Function to apply row highlighting
def highlight_row(row):
    if row["Result"].lower() != "sorry":
        return ["background-color: green"] * len(row)
    return [""] * len(row)


# Streamlit app
def main():
    st.title("📊 IPO Allotment Checker")

    # Add passcode protection
    st.sidebar.header("Access Control")
    passcode = st.sidebar.text_input("Enter Passcode", type="password")

    if passcode != PASSCODE:
        st.sidebar.error("Incorrect passcode. Please try again.")
        st.stop()  # Stop the app if the passcode is incorrect

    # Fetch IPO data
    with st.spinner("Fetching IPO data..."):
        ipo_data = fetch_ipo_data()
        if not ipo_data:
            st.error("Failed to fetch IPO data. Please try again later.")
            return

    # Create a multiselect dropdown for IPO names and registrars
    st.subheader("Select IPOs")
    include_all = st.checkbox("Include all IPOs?")
    if include_all:
        selected_items = [f"{item['name']} ({item['registrar']})" for item in ipo_data]
    else:
        options = [f"{item['name']} ({item['registrar']})" for item in ipo_data]
        selected_items = st.multiselect("Choose IPOs", options)

    # Get PAN numbers input (multiple PANs, one per line)
    st.subheader("Enter PAN Numbers")
    pan_numbers = st.text_area(
        "Enter one PAN number per line",
        height=150,
        placeholder="ABCDE1234F\nPQRST5678G\n...",
        help="Enter multiple PAN numbers, one per line.",
    )
    pan_numbers = [pan.strip() for pan in pan_numbers.split("\n") if pan.strip()]

    if st.button("Check Allotment", type="primary"):
        if not pan_numbers:
            st.error("Please enter at least one PAN number.")
            return

        invalid_pans = [pan for pan in pan_numbers if not validate_pan(pan)]
        if invalid_pans:
            st.error(
                f"Invalid PAN numbers: {', '.join(invalid_pans)}. Please enter valid 10-character PANs."
            )
            return

        # Process each PAN number separately
        for pan_number in pan_numbers:
            st.markdown(f"---")
            st.subheader(f"🔍 Results for PAN: `{pan_number}`")
            results = []

            for item in selected_items:
                # Extract name and registrar from the selected item
                name, registrar = item.split(" (")
                registrar = registrar[:-1]  # Remove the closing bracket

                # Find the corresponding company_id
                company_id = next(
                    (ipo["company_id"] for ipo in ipo_data if ipo["name"] == name), None
                )
                if not company_id:
                    st.error(f"Company ID not found for {name}.")
                    continue

                # Fetch allotment data
                with st.spinner(f"Fetching data for {name} (PAN: {pan_number})..."):
                    allotment_data = fetch_allotment_data(
                        registrar, company_id, pan_number
                    )
                    if allotment_data:
                        results.append(
                            {
                                "IPO Name": name,
                                "Registrar": registrar,
                                "Result": allotment_data.get("title", "N/A"),
                                "Status": allotment_data.get("text", "N/A"),
                            }
                        )
                    else:
                        st.warning(
                            f"No allotment data found for {name} (PAN: {pan_number})."
                        )

            # Display results for the current PAN number
            if results:
                df = pd.DataFrame(
                    results, index=range(1, len(results) + 1)
                )  # Start index from 1
                styled_df = df.style.apply(
                    highlight_row, axis=1
                )  # Apply row highlighting
                st.dataframe(
                    styled_df, use_container_width=True
                )  # Make the table responsive
            else:
                st.info(f"No allotment data found for PAN: `{pan_number}`.")


if __name__ == "__main__":
    main()
import streamlit as st
import requests
import pandas as pd

# API URLs
API_URL = st.secrets["API_URL"]
API_URL2_BASE = st.secrets["API_URL2_BASE"]

PASSCODE = st.secrets["PASSCODE"]


# Retry mechanism for API calls
def fetch_data(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from {url}: {e}")
        return None


# Fetch IPO data from the first API
@st.cache_data(ttl=600)  # Cache IPO data for 10 minutes
def fetch_ipo_data():
    data = fetch_data(API_URL)
    if data and data.get("status"):
        return data["data"]
    return []


# Fetch allotment data from the second API
def fetch_allotment_data(registrar, company_id, pan_number):
    url = f"{API_URL2_BASE}/{registrar}?company_id={company_id}&pan={pan_number}"
    data = fetch_data(url)
    if data and data.get("status"):
        return data["data"]
    return None


# Validate PAN number format (basic validation)
def validate_pan(pan_number):
    if not pan_number or len(pan_number) != 10 or not pan_number.isalnum():
        return False
    return True


# Function to apply row highlighting
def highlight_row(row):
    if row["Result"].lower() != "sorry":
        return ["background-color: green"] * len(row)
    return [""] * len(row)


# Streamlit app
def main():
    st.title("📊 IPO Allotment Checker")

    # Add passcode protection
    st.sidebar.header("Access Control")
    passcode = st.sidebar.text_input("Enter Passcode", type="password")

    if passcode != PASSCODE:
        st.sidebar.error("Incorrect passcode. Please try again.")
        st.stop()  # Stop the app if the passcode is incorrect

    # Fetch IPO data
    with st.spinner("Fetching IPO data..."):
        ipo_data = fetch_ipo_data()
        if not ipo_data:
            st.error("Failed to fetch IPO data. Please try again later.")
            return

    # Create a multiselect dropdown for IPO names and registrars
    st.subheader("Select IPOs")
    include_all = st.checkbox("Include all IPOs?")
    if include_all:
        selected_items = [f"{item['name']} ({item['registrar']})" for item in ipo_data]
    else:
        options = [f"{item['name']} ({item['registrar']})" for item in ipo_data]
        selected_items = st.multiselect("Choose IPOs", options)

    # Get PAN numbers input (multiple PANs, one per line)
    st.subheader("Enter PAN Numbers")
    pan_numbers = st.text_area(
        "Enter one PAN number per line",
        height=150,
        placeholder="ABCDE1234F\nPQRST5678G\n...",
        help="Enter multiple PAN numbers, one per line.",
    )
    pan_numbers = [pan.strip() for pan in pan_numbers.split("\n") if pan.strip()]

    if st.button("Check Allotment", type="primary"):
        if not pan_numbers:
            st.error("Please enter at least one PAN number.")
            return

        invalid_pans = [pan for pan in pan_numbers if not validate_pan(pan)]
        if invalid_pans:
            st.error(
                f"Invalid PAN numbers: {', '.join(invalid_pans)}. Please enter valid 10-character PANs."
            )
            return

        # Process each PAN number separately
        for pan_number in pan_numbers:
            st.markdown(f"---")
            st.subheader(f"🔍 Results for PAN: `{pan_number}`")
            results = []

            for item in selected_items:
                # Extract name and registrar from the selected item
                name, registrar = item.split(" (")
                registrar = registrar[:-1]  # Remove the closing bracket

                # Find the corresponding company_id
                company_id = next(
                    (ipo["company_id"] for ipo in ipo_data if ipo["name"] == name), None
                )
                if not company_id:
                    st.error(f"Company ID not found for {name}.")
                    continue

                # Fetch allotment data
                with st.spinner(f"Fetching data for {name} (PAN: {pan_number})..."):
                    allotment_data = fetch_allotment_data(
                        registrar, company_id, pan_number
                    )
                    if allotment_data:
                        results.append(
                            {
                                "IPO Name": name,
                                "Registrar": registrar,
                                "Result": allotment_data.get("title", "N/A"),
                                "Status": allotment_data.get("text", "N/A"),
                            }
                        )
                    else:
                        st.warning(
                            f"No allotment data found for {name} (PAN: {pan_number})."
                        )

            # Display results for the current PAN number
            if results:
                df = pd.DataFrame(
                    results, index=range(1, len(results) + 1)
                )  # Start index from 1
                styled_df = df.style.apply(
                    highlight_row, axis=1
                )  # Apply row highlighting
                st.dataframe(
                    styled_df, use_container_width=True
                )  # Make the table responsive
            else:
                st.info(f"No allotment data found for PAN: `{pan_number}`.")


if __name__ == "__main__":
    main()
