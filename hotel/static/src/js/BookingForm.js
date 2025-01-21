import { Component } from 'owl';
import { useState } from 'owl.hooks';

class RoomBookingForm extends Component {
    setup() {
        this.state = useState({
            checkinDate: '',
            checkoutDate: '',
            roomType: 'single',
            selectedRoom: null,
            selectedServices: [],
        });

        this.handleCheckInChange = this.handleCheckInChange.bind(this);
        this.handleCheckOutChange = this.handleCheckOutChange.bind(this);
        this.handleRoomSelect = this.handleRoomSelect.bind(this);
        this.handleServiceChange = this.handleServiceChange.bind(this);
    }

    handleCheckInChange(event) {
        this.state.checkinDate = event.target.value;
    }

    handleCheckOutChange(event) {
        this.state.checkoutDate = event.target.value;
    }

    handleRoomSelect(room) {
        this.state.selectedRoom = room;
    }

    handleServiceChange(service) {
        if (this.state.selectedServices.includes(service)) {
            this.state.selectedServices = this.state.selectedServices.filter(item => item !== service);
        } else {
            this.state.selectedServices.push(service);
        }
    }

    render() {
        return (
            <div>
                <h3>Book a Room</h3>
                <label>Check-in Date</label>
                <input type="date" value={this.state.checkinDate} onChange={this.handleCheckInChange} />
                <label>Check-out Date</label>
                <input type="date" value={this.state.checkoutDate} onChange={this.handleCheckOutChange} />
                
                <h4>Available Rooms</h4>
                {/* Render available rooms here */}
                {this.state.rooms.map(room => (
                    <div onClick={() => this.handleRoomSelect(room)}>
                        {room.room_code} - {room.price}
                    </div>
                ))}

                <h4>Services</h4>
                <div>
                    <input type="checkbox" onChange={() => this.handleServiceChange('wifi')} /> WiFi
                    <input type="checkbox" onChange={() => this.handleServiceChange('laundry')} /> Laundry
                </div>

                <button onClick={this.handleSubmit}>Book Now</button>
            </div>
        );
    }

    handleSubmit() {
        // Call API to create booking and pass selected room and services
    }
}

export default RoomBookingForm;
