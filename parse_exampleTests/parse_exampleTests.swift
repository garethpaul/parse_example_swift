//
//  parse_exampleTests.swift
//  parse_exampleTests
//
//  Created by Gareth Paul Jones on 6/3/14.
//  Copyright (c) 2014 Gareth Paul Jones. All rights reserved.
//

import Foundation
import XCTest

class parse_exampleTests: XCTestCase {
    
    override func setUp() {
        super.setUp()
        // Put setup code here. This method is called before the invocation of each test method in the class.
    }
    
    override func tearDown() {
        // Put teardown code here. This method is called after the invocation of each test method in the class.
        super.tearDown()
    }
    
    func testAppBundleIdentifierIsConfigured() {
        let identifier = NSBundle.mainBundle().bundleIdentifier
        XCTAssertNotNil(identifier, "Bundle identifier should be configured.")
        if let identifier = identifier {
            XCTAssertFalse(identifier.isEmpty, "Bundle identifier should not be empty.")
        }
    }
    
}
